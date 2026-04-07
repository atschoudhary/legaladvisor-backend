from openai import OpenAI
from typing import List, Dict
from config import settings
import logging
import re

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
1. **Direct Answer**: Start with a clear, direct answer to the question
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

            web_updates = self._format_latest_web_updates(results)
            if web_updates:
                answer = self._remove_latest_web_updates_section(answer)
                answer = f"{web_updates}\n\n{answer.strip()}"
            
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

    def _format_latest_web_updates(self, results: List[Dict]) -> str:
        """
        Build a deterministic latest-data section from web results.
        """
        web_results = [r for r in results if r.get("is_web_result")]
        if not web_results:
            return ""

        lines = ["## Latest Web Updates", "- Priority: The latest verified web information is listed first."]
        for result in web_results[:3]:
            source = result.get("source", "Web Search Result")
            published_date = result.get("published_date") or "Unknown publish date"
            retrieved_at = result.get("retrieved_at") or "Unknown retrieval time"
            source_url = result.get("source_url") or "No URL available"
            lines.append(f"- {source} | Published: {published_date} | Retrieved: {retrieved_at} | {source_url}")

        return "\n".join(lines)

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
