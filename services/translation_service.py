from openai import OpenAI
from typing import Optional
from config import settings
import logging

logger = logging.getLogger(__name__)

class TranslationService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    def detect_and_translate_query(self, query: str, target_language: Optional[str] = None) -> tuple[str, str]:
        """
        Detect query language and translate to English if needed
        Returns: (translated_query, detected_language)
        """
        try:
            # Detect language and translate if not English
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a language detector and translator for legal queries.
                        
If the query is in English, respond with:
LANGUAGE: english
QUERY: [original query]

If the query is in Urdu, respond with:
LANGUAGE: urdu
QUERY: [translated English query]

If the query is in Punjabi (Pakistani Punjabi/Shahmukhi script), respond with:
LANGUAGE: punjabi
QUERY: [translated English query]

If the query is in Sindhi, respond with:
LANGUAGE: sindhi
QUERY: [translated English query]

IMPORTANT: For Punjabi, recognize Pakistani Punjabi written in Shahmukhi (Urdu-based) script, not Indian Punjabi in Gurmukhi script.

Keep legal terminology accurate."""
                    },
                    {
                        "role": "user",
                        "content": query
                    }
                ],
                temperature=0.3
            )
            
            content = response.choices[0].message.content.strip()
            lines = content.split('\n')
            
            detected_language = "english"
            translated_query = query
            
            for line in lines:
                if line.startswith("LANGUAGE:"):
                    detected_language = line.split(":", 1)[1].strip().lower()
                elif line.startswith("QUERY:"):
                    translated_query = line.split(":", 1)[1].strip()
            
            logger.info(f"Detected language: {detected_language}")
            if detected_language != "english":
                logger.info(f"Translated query: {translated_query}")
            
            return translated_query, detected_language
            
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return query, "english"
    
    def translate_results(self, results: list, target_language: str) -> list:
        """
        Translate search results to target language - REMOVED
        Results are no longer translated, only the synthesized answer
        """
        return results

translation_service = TranslationService()
