from openai import OpenAI
from config import settings
import logging

logger = logging.getLogger(__name__)

class MultilingualChatService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    def detect_language(self, text: str) -> str:
        """
        Detect language of input text
        Returns: english, urdu, punjabi, sindhi, or roman_urdu
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": """Detect the language and respond with ONLY ONE of these:
- english
- urdu
- punjabi (Pakistani Punjabi/Shahmukhi script)
- sindhi
- roman_urdu (Urdu written in English alphabet)

Respond with just the language name, nothing else."""
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ],
                temperature=0.3,
                max_tokens=10
            )
            
            language = response.choices[0].message.content.strip().lower()
            logger.info(f"Detected language: {language}")
            return language
            
        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            return "english"
    
    def chat(self, user_message: str, conversation_history: list = None) -> dict:
        """
        Process chat message and respond in the same language
        Returns: {response: str, language: str}
        """
        try:
            # Detect language
            detected_language = self.detect_language(user_message)
            
            language_names = {
                "english": "English",
                "urdu": "Urdu",
                "punjabi": "Pakistani Punjabi (Shahmukhi script)",
                "sindhi": "Sindhi",
                "roman_urdu": "Roman Urdu (Urdu written in English alphabet)"
            }
            
            target_language = language_names.get(detected_language, "English")
            
            # Build messages
            messages = [
                {
                    "role": "system",
                    "content": f"""You are LegalAdvisor, an AI assistant specializing in Pakistani law and general assistance.

CRITICAL RULES:
1. Always respond in {target_language} (the same language as the user's input)
2. Provide accurate, helpful information
3. Use markdown formatting for better readability
4. Be professional and courteous
5. For legal questions, provide information but never give legal advice
6. If you don't know something, admit it

MARKDOWN FORMATTING:
- Use **bold** for emphasis
- Use ## for main sections
- Use - for bullet points
- Use numbered lists for steps"""
                }
            ]
            
            # Add conversation history if provided
            if conversation_history:
                messages.extend(conversation_history)
            
            # Add current user message
            messages.append({
                "role": "user",
                "content": user_message
            })
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )
            
            assistant_response = response.choices[0].message.content
            
            logger.info(f"Chat response generated in {detected_language}")
            
            return {
                "response": assistant_response,
                "language": detected_language
            }
            
        except Exception as e:
            logger.error(f"Chat failed: {e}")
            raise Exception(f"Failed to process chat: {str(e)}")
    
    def chat_stream(self, user_message: str, conversation_history: list = None):
        """
        Process chat message with streaming response
        Yields response chunks
        """
        try:
            detected_language = self.detect_language(user_message)
            
            language_names = {
                "english": "English",
                "urdu": "Urdu",
                "punjabi": "Pakistani Punjabi (Shahmukhi script)",
                "sindhi": "Sindhi",
                "roman_urdu": "Roman Urdu (Urdu written in English alphabet)"
            }
            
            target_language = language_names.get(detected_language, "English")
            
            messages = [
                {
                    "role": "system",
                    "content": f"""You are LegalAdvisor, an AI assistant specializing in Pakistani law and general assistance.

CRITICAL RULES:
1. Always respond in {target_language} (the same language as the user's input)
2. Provide accurate, helpful information
3. Use markdown formatting for better readability
4. Be professional and courteous
5. For legal questions, provide information but never give legal advice

MARKDOWN FORMATTING:
- Use **bold** for emphasis
- Use ## for main sections
- Use - for bullet points"""
                }
            ]
            
            if conversation_history:
                messages.extend(conversation_history)
            
            messages.append({
                "role": "user",
                "content": user_message
            })
            
            stream = self.client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                temperature=0.7,
                max_tokens=2000,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
            
            logger.info(f"Chat stream completed in {detected_language}")
            
        except Exception as e:
            logger.error(f"Chat stream failed: {e}")
            raise Exception(f"Failed to process chat stream: {str(e)}")

multilingual_chat_service = MultilingualChatService()
