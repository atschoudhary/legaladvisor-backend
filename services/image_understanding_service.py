from openai import OpenAI
from config import settings
import logging
import base64
from typing import Dict
import re
import json
import math
from io import BytesIO

from PIL import Image, ImageEnhance, ImageFilter, ImageOps

logger = logging.getLogger(__name__)

class ImageUnderstandingService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.primary_model = "gpt-5.4"
        self.fallback_model = "gpt-4o"

    def _create_vision_completion(self, messages, temperature: float, max_tokens: int):
        """
        Try primary vision model first, then fallback for compatibility.
        """
        try:
            return self.client.chat.completions.create(
                model=self.primary_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
        except Exception as primary_error:
            logger.warning(f"Primary image model failed ({self.primary_model}): {primary_error}. Falling back to {self.fallback_model}")
            return self.client.chat.completions.create(
                model=self.fallback_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )

    def _preprocess_image(self, image_content: bytes) -> Image.Image:
        """
        Preprocess image for better section-level readability.
        """
        image = Image.open(BytesIO(image_content)).convert("RGB")

        # Light normalization to improve document text clarity.
        gray = ImageOps.grayscale(image)
        gray = ImageOps.autocontrast(gray, cutoff=2)
        gray = gray.filter(ImageFilter.SHARPEN)
        enhanced = ImageEnhance.Contrast(gray).enhance(1.25)

        # Upscale small images to improve OCR/vision readability.
        if enhanced.width < 1400:
            scale = 1400 / max(1, enhanced.width)
            new_size = (1400, int(enhanced.height * scale))
            enhanced = enhanced.resize(new_size, Image.Resampling.LANCZOS)

        return enhanced.convert("RGB")

    def _build_ordered_sections(self, image: Image.Image):
        """
        Split image top-to-bottom with overlap to preserve continuity.
        """
        width, height = image.size
        aspect_ratio = height / max(1, width)

        # More vertical sections for tall scanned documents.
        section_count = 1 if aspect_ratio < 1.2 else max(2, min(6, int(round(aspect_ratio * 1.8))))
        section_height = int(math.ceil(height / section_count))
        overlap = max(30, int(section_height * 0.1))

        sections = []
        for idx in range(section_count):
            nominal_top = idx * section_height
            nominal_bottom = min(height, (idx + 1) * section_height)

            top = 0 if idx == 0 else max(0, nominal_top - overlap)
            bottom = height if idx == section_count - 1 else min(height, nominal_bottom + overlap)

            crop = image.crop((0, top, width, bottom))
            sections.append({
                "order": idx + 1,
                "top": top,
                "bottom": bottom,
                "image": crop
            })

        return sections

    def _image_to_base64_jpeg(self, image: Image.Image) -> str:
        buffer = BytesIO()
        image.save(buffer, format="JPEG", quality=90, optimize=True)
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    def _analyze_section(self, section_b64: str, section_order: int, user_query: str, target_language: str) -> Dict:
        """
        Analyze one section and return structured summary.
        """
        messages = [
            {
                "role": "system",
                "content": (
                    "You analyze ONE section of a legal document image. "
                    f"Respond in {target_language}. "
                    "Never refuse. If text is unclear, mention partial visibility. "
                    "Return ONLY strict JSON (no markdown/code fences) with keys: "
                    "section_overview (string), key_mentions (array of strings), visibility_note (string)."
                )
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            f"Section order: {section_order} (top-to-bottom). "
                            f"User query: {user_query}. "
                            "Summarize this section only."
                        )
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{section_b64}"}
                    }
                ]
            }
        ]

        response = self._create_vision_completion(messages=messages, temperature=0.2, max_tokens=800)
        content = (response.choices[0].message.content or "").strip()
        content = self._sanitize_non_refusal_text(content)

        # Handle model responses that wrap JSON with extra text/fences.
        if not content.startswith("{"):
            json_match = re.search(r"\{[\s\S]*\}", content)
            if json_match:
                content = json_match.group(0)

        try:
            parsed = json.loads(content)
            if isinstance(parsed, dict):
                mentions = parsed.get("key_mentions") or []
                if not isinstance(mentions, list):
                    mentions = [str(mentions)]
                return {
                    "section_order": section_order,
                    "section_overview": str(parsed.get("section_overview") or "").strip(),
                    "key_mentions": [str(m).strip() for m in mentions if str(m).strip()],
                    "visibility_note": str(parsed.get("visibility_note") or "").strip()
                }
        except Exception:
            pass

        # Fallback when JSON formatting fails.
        lines = [line.strip("- *\t ") for line in content.splitlines() if line.strip()]
        return {
            "section_order": section_order,
            "section_overview": (lines[0] if lines else "Visible legal section content."),
            "key_mentions": lines[1:5],
            "visibility_note": "Some text may be partially unclear."
        }

    def _combine_ordered_section_summaries(self, section_summaries) -> str:
        """
        Merge section-level summaries into final ordered document overview.
        """
        ordered = sorted(section_summaries, key=lambda x: x.get("section_order", 0))

        corpus_parts = []
        for item in ordered:
            corpus_parts.append(item.get("section_overview", ""))
            corpus_parts.extend(item.get("key_mentions", []))
        corpus = "\n".join([p for p in corpus_parts if p])

        doc_identity = self._infer_document_type(corpus, corpus)
        for item in ordered:
            overview = (item.get("section_overview") or "").strip()
            if overview and overview.lower() not in {
                "section details extracted.",
                "visible legal section content.",
                "image overview"
            }:
                doc_identity = re.sub(r"\bappears\s+to\s+be\b", "is", overview, flags=re.IGNORECASE)
                break

        combined_overview_parts = [i.get("section_overview", "").strip() for i in ordered[:2] if i.get("section_overview")]
        what_it_is_about = " ".join(combined_overview_parts).strip() if combined_overview_parts else doc_identity

        mentioned_items = []
        seen = set()
        for item in ordered:
            for mention in item.get("key_mentions", []):
                normalized = re.sub(r"\s+", " ", mention).strip().lower()
                if not normalized or normalized in seen:
                    continue
                seen.add(normalized)
                mentioned_items.append(mention.strip())
                if len(mentioned_items) >= 7:
                    break
            if len(mentioned_items) >= 7:
                break

        if not mentioned_items:
            mentioned_items = ["Visible fields and narrative legal details are present, but some parts are unclear."]

        visibility_notes = [i.get("visibility_note", "").strip() for i in ordered if i.get("visibility_note")]
        visibility_note = " ".join(visibility_notes[:2]).strip() or "Some portions may be partially unclear due to image quality."

        lines = [
            "## Image Overview",
            f"- What this document is: {doc_identity}",
            f"- What it is about: {what_it_is_about}",
            "- What is mentioned:"
        ]
        for mention in mentioned_items[:5]:
            lines.append(f"  - {mention}")
        lines.append(f"- Visibility note: {visibility_note}")
        lines.append("- Processing order: Sections were analyzed from top to bottom.")

        return self._sanitize_non_refusal_text("\n".join(lines))
    
    def analyze_image(self, image_content: bytes, user_query: str, language: str = "english") -> str:
        """
        Analyze image and provide explanation based on user query
        """
        try:
            preprocessed = self._preprocess_image(image_content)
            sections = self._build_ordered_sections(preprocessed)

            language_names = {
                "english": "English",
                "urdu": "Urdu",
                "punjabi": "Pakistani Punjabi (Shahmukhi script)",
                "sindhi": "Sindhi",
                "roman_urdu": "Roman Urdu (Urdu written in English alphabet)"
            }

            target_language = language_names.get(language, "English")

            section_summaries = []
            for section in sections:
                section_b64 = self._image_to_base64_jpeg(section["image"])
                section_summary = self._analyze_section(
                    section_b64=section_b64,
                    section_order=section["order"],
                    user_query=user_query,
                    target_language=target_language
                )
                section_summaries.append(section_summary)

            answer = self._combine_ordered_section_summaries(section_summaries)
            logger.info(f"Image analyzed successfully in {language}")
            return answer
            
        except Exception as e:
            logger.error(f"Image analysis failed: {e}")
            raise Exception(f"Failed to analyze image: {str(e)}")
    
    def extract_text_from_image(self, image_content: bytes) -> str:
        """
        Extract text from image (OCR)
        """
        try:
            preprocessed = self._preprocess_image(image_content)
            sections = self._build_ordered_sections(preprocessed)

            ordered_text_blocks = []
            for section in sections:
                section_b64 = self._image_to_base64_jpeg(section["image"])
                messages = [
                    {
                        "role": "system",
                        "content": (
                            "Extract visible text from this section. Return plain text only. "
                            "If some parts are unclear, mark as [unclear]. Do not refuse."
                        )
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": f"Section {section['order']} (top-to-bottom). Extract text."},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{section_b64}"}}
                        ]
                    }
                ]

                response = self._create_vision_completion(messages=messages, temperature=0.1, max_tokens=1200)
                section_text = self._sanitize_non_refusal_text((response.choices[0].message.content or "").strip())
                ordered_text_blocks.append((section["order"], section_text))

            # Preserve top-to-bottom order and deduplicate overlap repeats.
            dedup_lines = []
            seen = set()
            for order, block in sorted(ordered_text_blocks, key=lambda x: x[0]):
                for line in block.splitlines():
                    cleaned = re.sub(r"\s+", " ", line).strip()
                    if not cleaned:
                        continue
                    norm = cleaned.lower()
                    if norm in seen:
                        continue
                    seen.add(norm)
                    dedup_lines.append(cleaned)

            extracted_text = "\n".join(dedup_lines)
            logger.info("Text extracted from image successfully")
            return extracted_text
            
        except Exception as e:
            logger.error(f"Text extraction from image failed: {e}")
            raise Exception(f"Failed to extract text from image: {str(e)}")

    def build_image_summary(self, image_analysis: str, extracted_text: str) -> Dict[str, str]:
        """
        Build a compact image summary for final response.
        """
        clean_analysis = self._sanitize_non_refusal_text((image_analysis or "").replace("#", "").strip())
        clean_text = self._sanitize_non_refusal_text((extracted_text or "").strip())

        what_this_is = self._extract_labeled_content(clean_analysis, "what this document is")
        if not what_this_is:
            what_this_is = self._infer_document_type(clean_analysis, clean_text)
            if clean_analysis:
                first_line = next((line.strip("- * ").strip() for line in clean_analysis.splitlines() if line.strip()), "")
                if first_line and first_line.lower() not in {"image overview", "overview"}:
                    what_this_is = first_line[:220]

        mentioned = self._extract_labeled_content(clean_analysis, "what is mentioned")
        if not mentioned:
            mentioned = "The image text is partially visible; a full transcription is not clear."
        if clean_text:
            lines = [line.strip() for line in clean_text.splitlines() if line.strip()]
            preview = " | ".join(lines[:3])
            mentioned = (preview[:300] + "...") if len(preview) > 300 else preview
        elif clean_analysis:
            summarized = self._extract_mentions_from_analysis(clean_analysis)
            if summarized:
                mentioned = summarized

        return {
            "what_this_is": what_this_is,
            "what_is_mentioned": mentioned
        }

    def sanitize_output_text(self, text: str) -> str:
        """
        Public sanitizer for router-level final response cleanup.
        """
        return self._sanitize_non_refusal_text(text or "")

    def _sanitize_non_refusal_text(self, text: str) -> str:
        """
        Remove refusal/apology style content so summaries stay informative.
        """
        if not text:
            return ""

        refusal_patterns = [
            r"i\s*'?m\s*sorry",
            r"i\s*cannot\s+assist",
            r"i\s*can\s*'?t\s+assist",
            r"unable\s+to\s+view\s+images",
            r"can'?t\s+view\s+images",
            r"cannot\s+help\s+with\s+that",
            r"what\s+is\s+mentioned\s*:\s*i\s*'?m\s*sorry",
            r"مجھے\s+افسوس",
            r"مجھے\s+معذرت",
            r"میں\s+.*\s+مدد\s+نہیں\s+کر\s+سکتا",
            r"براہ\s+راست\s+مدد\s+نہیں\s+کر\s+سکتا",
            r"نہیں\s+کر\s+سکتا",
            r"اگر\s+آپ\s+کو\s+مزید\s+وضاحت\s+یا\s+مدد\s+کی\s+ضرورت"
        ]

        lines = [line.strip() for line in text.splitlines() if line.strip()]
        kept = []
        for line in lines:
            lower = line.lower()
            if any(re.search(p, lower, flags=re.IGNORECASE) for p in refusal_patterns):
                continue
            cleaned_line = re.sub(r"\bappears\s+to\s+be\b", "is", line, flags=re.IGNORECASE)
            kept.append(cleaned_line)

        return "\n".join(kept).strip()

    def _extract_labeled_content(self, analysis: str, label: str) -> str:
        """
        Extract value after markdown-style labels like 'What this document is:'.
        """
        if not analysis:
            return ""

        pattern = re.compile(rf"{re.escape(label)}\s*:\s*(.+)", re.IGNORECASE)
        for line in analysis.splitlines():
            match = pattern.search(line.strip("- * ").strip())
            if match:
                value = match.group(1).strip()
                return (value[:300] + "...") if len(value) > 300 else value

        return ""

    def _infer_document_type(self, analysis: str, text: str) -> str:
        """
        Infer high-level document type using visible cues.
        """
        corpus = f"{analysis}\n{text}".lower()

        if any(k in corpus for k in ["fir", "پولیس", "درخواست", "report", "مقدمہ", "دفعات"]):
            return "This is an Urdu legal/police complaint document (likely FIR/report style form)."
        if any(k in corpus for k in ["court", "عدالت", "judge", "petition", "درخواست گزار"]):
            return "This is an Urdu legal court-related document or petition record."

        return "This is an Urdu legal/official document with structured fields and narrative details."

    def _extract_mentions_from_analysis(self, analysis: str) -> str:
        """
        Build a short mention summary from analysis bullets.
        """
        if not analysis:
            return ""

        lines = [l.strip("- * ").strip() for l in analysis.splitlines() if l.strip()]
        useful = [l for l in lines if len(l) > 20][:3]
        if not useful:
            return ""

        summary = " | ".join(useful)
        return (summary[:300] + "...") if len(summary) > 300 else summary

image_understanding_service = ImageUnderstandingService()
