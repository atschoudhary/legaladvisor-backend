from openai import OpenAI
from typing import List, Dict
from config import settings
import logging
import re
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class AnswerSynthesisService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        self.system_prompt = """You are LegalAdvisor, an expert AI legal assistant specializing in Pakistani law.

Your role is to provide accurate, comprehensive, and well-structured legal answers based on the search results provided.

CRITICAL RULES:
1. ONLY use information from the provided search results
2. DO NOT make up or infer legal information not present in the results
3. If results are insufficient, clearly state what information is missing
4. If web search results are present, include a short "Latest Web Updates" section
5. Maintain professional legal language appropriate for the query language
6. Structure your answer clearly with sections when appropriate
7. Use markdown formatting for better readability

ANSWER STRUCTURE (use markdown):
1. **Summary**: Start with a clear summary to the question
2. **Latest Legal Position**: Prioritize the most recent legal developments first
3. **Legal Basis**: Explain the relevant laws, acts, or provisions
4. **Key Points**: Break down important details using bullet points
5. **Additional Context**: Provide relevant context if helpful

LANGUAGE RULES:
- If query is in English, respond in English
- If query is in Urdu (اردو), respond in Urdu
- If query is in Punjabi (Pakistani Punjabi/Shahmukhi script), respond in Pakistani Punjabi using Shahmukhi script
- If query is in Sindhi (سنڌي), respond in Sindhi
- Maintain legal terminology accuracy in all languages
- Use formal, professional tone appropriate for legal content

MARKDOWN FORMATTING:
- Use **bold** for emphasis and important terms
- Use ## for main sections
- Use ### for subsections
- Use bullet points (-) for lists
- Use numbered lists (1., 2., 3.) for sequential steps
- Use > for important quotes or legal provisions

IMPORTANT:
- When web data exists, include concise source attribution (name/date/link if available)
- Do not repeat sections or headings in the final answer
- Do not use the heading or phrase "Direct Answer"
- If the query asks for "this year" or current-year updates and no verified current-year implementations are present, explicitly say no implemented laws were verified for the current year in retrieved sources
- If results contradict each other, mention both perspectives without citing sources
- If results are from different provinces, clarify jurisdictional differences
- If information is outdated or unclear, mention this
- Never provide legal advice - only explain what the law states
- Focus on providing a clear, comprehensive answer without source references"""

    def synthesize_answer(
        self,
        query: str,
        results: List[Dict],
        detected_language: str
    ) -> Dict:
        """
        Generate a comprehensive answer based on search results
        """
        if not results:
            return {
                "answer": self._get_no_results_message(detected_language),
                "has_answer": False
            }
        
        try:
            # Prepare context from results
            context = self._prepare_context(results)
            
            # Generate answer
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": self.system_prompt
                    },
                    {
                        "role": "user",
                        "content": f"""Query: {query}

Search Results:
{context}

Please provide a comprehensive, well-structured answer to this legal query based on the search results above. Remember to:
1. Answer in the same language as the query
2. Only use information from the provided results
3. Cite your sources
4. Structure your answer clearly
5. Be precise and professional"""
                    }
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            answer = response.choices[0].message.content

            web_updates = self._format_latest_web_updates(query, results)
            if web_updates:
                answer = self._remove_latest_web_updates_section(answer)
                answer = self._remove_direct_answer_heading(answer)
                answer = f"{web_updates}\n\n{answer.strip()}"
            else:
                answer = self._remove_direct_answer_heading(answer)

            answer = self._linkify_main_body_web_references(answer, results)
            
            logger.info(f"Generated answer for query in {detected_language}")
            
            return {
                "answer": answer,
                "has_answer": True,
                "sources_used": len(results)
            }
            
        except Exception as e:
            logger.error(f"Answer synthesis failed: {e}")
            return {
                "answer": self._get_error_message(detected_language),
                "has_answer": False
            }
    
    def _prepare_context(self, results: List[Dict]) -> str:
        """
        Prepare search results as context for LLM
        """
        context_parts = []
        
        for idx, result in enumerate(results, 1):
            source_type = "Web Search" if result.get("is_web_result") else result.get("source", "Unknown")
            province = result.get("province", "N/A")
            text = result.get("text", "")
            source_url = result.get("source_url") or "N/A"
            published_date = result.get("published_date") or "N/A"
            retrieved_at = result.get("retrieved_at") or "N/A"
            
            context_parts.append(f"""
[Result {idx}]
Source: {source_type}
Province: {province}
URL: {source_url}
Published Date: {published_date}
Retrieved At: {retrieved_at}
Content: {text}
---""")
        
        return "\n".join(context_parts)

    def _format_latest_web_updates(self, query: str, results: List[Dict]) -> str:
        """
        Build a deterministic latest-data section from web results.
        """
        web_results = [r for r in results if r.get("is_web_result")]
        if not web_results:
            return ""

        current_year = datetime.now(timezone.utc).year
        this_year_query = self._is_this_year_query(query)
        latest_query = self._is_latest_query(query)
        prioritize_current_year = this_year_query or latest_query
        selected_results = web_results

        if prioritize_current_year:
            selected_results = [
                r for r in web_results
                if self._extract_year_from_result(r) == current_year
            ]

        lines = [
            "## Latest Web Updates",
            "- Priority: The latest verified legal implementations are listed first.",
            f"- Target Year: {current_year}"
        ]

        if prioritize_current_year and not selected_results:
            lines.append(f"- No verified newly implemented laws were found for {current_year} in the retrieved web sources.")
            return "\n".join(lines)

        for result in selected_results[:3]:
            source = result.get("source", "Web Search Result")
            published_date = result.get("published_date") or "Unknown publish date"
            retrieved_at = result.get("retrieved_at") or "Unknown retrieval time"
            source_url = result.get("source_url") or "No URL available"
            summary = self._build_latest_item_description(result)

            if source_url and source_url != "No URL available":
                source_label = f"[{source}]({source_url})"
            else:
                source_label = source

            lines.append(f"- {source_label} | Published: {published_date} | Retrieved: {retrieved_at}")
            lines.append(f"  Summary: {summary}")

        return "\n".join(lines)

    def _is_latest_query(self, query: str) -> bool:
        """
        Detect if user asks for latest/recent implementations.
        """
        if not query:
            return False

        q = query.lower()
        patterns = [
            r"\blatest\b",
            r"\brecent\b",
            r"\bnew\b",
            r"\bnewly\s+implemented\b",
            r"\bimplemented\s+this\s+year\b"
        ]
        return any(re.search(p, q) for p in patterns)

    def _is_this_year_query(self, query: str) -> bool:
        """
        Detect if user asks specifically for current-year updates.
        """
        if not query:
            return False

        q = query.lower()
        patterns = [
            r"\bthis\s+year\b",
            r"\bcurrent\s+year\b",
            r"\biss\s+saal\b",
            r"\bis\s+saal\b",
            r"\bاس\s+سال\b"
        ]
        return any(re.search(p, q) for p in patterns)

    def _extract_year_from_result(self, result: Dict) -> int:
        """
        Infer a year from published date, URL, or text when available.
        """
        candidate_fields = [
            str(result.get("published_date") or ""),
            str(result.get("source_url") or ""),
            str(result.get("text") or "")[:500]
        ]

        for field in candidate_fields:
            match = re.search(r"\b(20\d{2})\b", field)
            if match:
                return int(match.group(1))

        return 0

    def _build_latest_item_description(self, result: Dict) -> str:
        """
        Build a concise one-line summary for each latest web item.
        """
        summary = str(result.get("summary") or "").strip()
        if summary:
            return summary

        text = str(result.get("text") or "")
        text = re.sub(r"\s+", " ", text).strip()
        if not text:
            return "No additional source description available."

        sentence_match = re.search(r"(.{40,220}?[.!?])", text)
        if sentence_match:
            return sentence_match.group(1).strip()

        return (text[:220] + "...") if len(text) > 220 else text

    def _remove_latest_web_updates_section(self, answer: str) -> str:
        """
        Remove any model-generated Latest Web Updates section to avoid duplicates.
        """
        if not answer:
            return ""

        lines = answer.splitlines()
        start_idx = None
        heading_pattern = re.compile(r"^#{0,3}\s*latest\s+web\s+updates\s*$", re.IGNORECASE)

        for idx, line in enumerate(lines):
            if heading_pattern.match(line.strip()):
                start_idx = idx
                break

        if start_idx is None:
            return answer.strip()

        cleaned = "\n".join(lines[:start_idx]).strip()
        return cleaned or answer.strip()

    def _remove_direct_answer_heading(self, answer: str) -> str:
        """
        Remove model heading variants like 'Direct Answer'.
        """
        if not answer:
            return ""

        patterns = [
            r"^\s*#{0,3}\s*direct\s+answer\s*\n+",
            r"^\s*\*\*\s*direct\s+answer\s*\*\*\s*\n+",
            r"^\s*direct\s+answer\s*\n+",
            r"(?im)^\s*#{1,3}\s*direct\s+answer\s*$",
            r"(?im)^\s*direct\s+answer\s*$"
        ]

        cleaned = answer
        for pattern in patterns:
            cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)

        return cleaned.strip()

    def _linkify_main_body_web_references(self, answer: str, results: List[Dict]) -> str:
        """
        Convert web references in the answer body to clickable markdown links.
        """
        if not answer:
            return ""

        linked = answer

        for result in [r for r in results if r.get("is_web_result") and r.get("source_url")]:
            source = str(result.get("source") or "").strip()
            source_url = str(result.get("source_url") or "").strip()
            if not source or not source_url:
                continue

            markdown_link = f"[{source}]({source_url})"
            if markdown_link in linked:
                continue
            linked = re.sub(rf"\b{re.escape(source)}\b", markdown_link, linked)

        # Linkify bare URLs that are not already part of markdown links.
        linked = re.sub(
            r"(?<!\()(?P<url>https?://[^\s)]+)",
            lambda m: f"[{m.group('url')}]({m.group('url')})",
            linked
        )

        return linked
    
    def _get_no_results_message(self, language: str) -> str:
        """
        Get no results message in appropriate language
        """
        messages = {
            "english": "I couldn't find any relevant legal documents for your query. Please try rephrasing your question or using different keywords.",
            "urdu": "میں آپ کے سوال کے لیے کوئی متعلقہ قانونی دستاویزات نہیں ڈھونڈ سکا۔ براہ کرم اپنے سوال کو دوبارہ لکھیں یا مختلف الفاظ استعمال کریں۔",
            "punjabi": "ਮੈਂ ਤੁਹਾਡੇ ਸਵਾਲ ਲਈ ਕੋਈ ਸੰਬੰਧਿਤ ਕਾਨੂੰਨੀ ਦਸਤਾਵੇਜ਼ ਨਹੀਂ ਲੱਭ ਸਕਿਆ। ਕਿਰਪਾ ਕਰਕੇ ਆਪਣੇ ਸਵਾਲ ਨੂੰ ਦੁਬਾਰਾ ਲਿਖੋ ਜਾਂ ਵੱਖਰੇ ਸ਼ਬਦ ਵਰਤੋ।",
            "sindhi": "مان توهان جي سوال لاءِ ڪو به لاڳاپيل قانوني دستاويز نه ڳولي سگهيو آهيان. مهرباني ڪري پنهنجي سوال کي ٻيهر لکو يا مختلف لفظ استعمال ڪريو۔"
        }
        return messages.get(language, messages["english"])
    
    def _get_error_message(self, language: str) -> str:
        """
        Get error message in appropriate language
        """
        messages = {
            "english": "I encountered an error while processing your query. Please try again.",
            "urdu": "آپ کے سوال پر کارروائی کرتے وقت مجھے ایک خرابی کا سامنا کرنا پڑا۔ براہ کرم دوبارہ کوشش کریں۔",
            "punjabi": "ਤੁਹਾਡੇ ਸਵਾਲ ਦੀ ਪ੍ਰਕਿਰਿਆ ਕਰਦੇ ਸਮੇਂ ਮੈਨੂੰ ਇੱਕ ਗਲਤੀ ਦਾ ਸਾਹਮਣਾ ਕਰਨਾ ਪਿਆ। ਕਿਰਪਾ ਕਰਕੇ ਦੁਬਾਰਾ ਕੋਸ਼ਿਸ਼ ਕਰੋ।",
            "sindhi": "توهان جي سوال تي عمل ڪرڻ دوران مون کي هڪ غلطي جو سامنا ٿيو. مهرباني ڪري ٻيهر ڪوشش ڪريو۔"
        }
        return messages.get(language, messages["english"])

answer_synthesis_service = AnswerSynthesisService()
