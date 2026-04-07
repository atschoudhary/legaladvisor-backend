from openai import OpenAI
from config import settings
import logging
import base64
from typing import Dict

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
                        "content": f"""You are an AI assistant that analyzes images and provides guidance.

Analyze the provided image and answer the user's question in {target_language}.

RULES:
1. Describe what you see in the image clearly
2. Provide relevant guidance or explanation
3. Use markdown formatting for better readability
4. Respond in {target_language}
5. If the image contains legal documents, maintain accuracy
6. Be specific and helpful

MARKDOWN FORMATTING:
- Use **bold** for important terms
- Use ## for main sections
- Use - for bullet points
- Use numbered lists for steps"""
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
                        "content": "Extract all text from this image. Provide only the extracted text, maintaining the original structure and formatting as much as possible."
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
        clean_analysis = (image_analysis or "").replace("#", "").strip()
        clean_text = (extracted_text or "").strip()

        what_this_is = "Image provided by user."
        if clean_analysis:
            first_line = next((line.strip("- * ").strip() for line in clean_analysis.splitlines() if line.strip()), "")
            if first_line:
                what_this_is = first_line[:220]

        mentioned = "No clear extracted text found."
        if clean_text:
            lines = [line.strip() for line in clean_text.splitlines() if line.strip()]
            preview = " | ".join(lines[:3])
            mentioned = (preview[:300] + "...") if len(preview) > 300 else preview

        return {
            "what_this_is": what_this_is,
            "what_is_mentioned": mentioned
        }

image_understanding_service = ImageUnderstandingService()
