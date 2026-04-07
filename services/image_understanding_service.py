from openai import OpenAI
from config import settings
import logging
import base64
from typing import Dict
import re

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
    
    def analyze_image(self, image_content: bytes, user_query: str, language: str = "english") -> str:
        """
        Analyze image and provide explanation based on user query
        """
        try:
            # Encode image to base64
            base64_image = base64.b64encode(image_content).decode('utf-8')
            
            language_names = {
                "english": "English",
                "urdu": "Urdu",
                "punjabi": "Pakistani Punjabi (Shahmukhi script)",
                "sindhi": "Sindhi",
                "roman_urdu": "Roman Urdu (Urdu written in English alphabet)"
            }
            
            target_language = language_names.get(language, "English")
            
            messages = [
                    {
                        "role": "system",
                                                "content": f"""You are an AI assistant that analyzes images and provides high-level document understanding.

Analyze the provided image and answer the user's question in {target_language}.

RULES:
1. Identify what type of document/image this is
2. Explain what the document is generally about (high-level)
3. List key visible items (headings/fields/types of details), not verbatim full transcription
4. If text is unclear, say it is partially unclear and still provide best-effort overall summary
5. Never respond with refusal/apology for normal document understanding tasks
6. Never include phrases like "I'm sorry, I can't assist with that"
7. Do not provide legal advice, only document understanding
8. Use markdown formatting for better readability
4. Respond in {target_language}
9. If the image contains legal documents, maintain accuracy
10. Be specific and helpful

MARKDOWN FORMATTING:
- Use ## Image Overview
- Use these bullet labels exactly:
    - What this document is
    - What it is about
    - What is mentioned
    - Visibility note"""
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"User Question: {user_query}\n\nPlease analyze this image and answer the question."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ]

            response = self._create_vision_completion(
                messages=messages,
                temperature=0.3,
                max_tokens=2000
            )
            
            answer = response.choices[0].message.content
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
            base64_image = base64.b64encode(image_content).decode('utf-8')
            
            messages = [
                    {
                        "role": "system",
                        "content": "Extract visible text from this image. Return plain text only. If some parts are unclear, mark them as [unclear] and continue with best-effort extraction. Do not refuse."
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Please extract all text from this image."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ]

            response = self._create_vision_completion(
                messages=messages,
                temperature=0.1,
                max_tokens=2000
            )
            
            extracted_text = response.choices[0].message.content
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

        what_this_is = self._infer_document_type(clean_analysis, clean_text)
        if clean_analysis:
            first_line = next((line.strip("- * ").strip() for line in clean_analysis.splitlines() if line.strip()), "")
            if first_line:
                what_this_is = first_line[:220]

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
            r"cannot\s+help\s+with\s+that",
            r"what\s+is\s+mentioned\s*:\s*i\s*'?m\s*sorry",
            r"مجھے\s+افسوس",
            r"میں\s+.*\s+مدد\s+نہیں\s+کر\s+سکتا",
            r"نہیں\s+کر\s+سکتا"
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
