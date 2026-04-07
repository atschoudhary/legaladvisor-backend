from openai import OpenAI
from config import settings
import logging
import io

logger = logging.getLogger(__name__)

class VoiceService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    def speech_to_text(self, audio_content: bytes, filename: str) -> dict:
        """
        Convert speech to text using OpenAI Whisper
        Returns: {text: str, language: str}
        """
        try:
            # Create a file-like object from bytes
            audio_file = io.BytesIO(audio_content)
            audio_file.name = filename
            
            # Transcribe audio
            transcript = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="verbose_json"
            )
            
            detected_language = transcript.language if hasattr(transcript, 'language') else 'unknown'
            text = transcript.text
            
            logger.info(f"Speech-to-text completed. Language: {detected_language}")
            
            return {
                "text": text,
                "language": detected_language
            }
            
        except Exception as e:
            logger.error(f"Speech-to-text failed: {e}")
            raise Exception(f"Failed to transcribe audio: {str(e)}")
    
    def text_to_speech(self, text: str, voice: str = "alloy") -> bytes:
        """
        Convert text to speech using OpenAI TTS
        Available voices: alloy, echo, fable, onyx, nova, shimmer
        Returns: audio bytes (MP3 format)
        """
        try:
            response = self.client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=text
            )
            
            # Get audio content as bytes
            audio_content = response.content
            
            logger.info(f"Text-to-speech completed. Voice: {voice}")
            
            return audio_content
            
        except Exception as e:
            logger.error(f"Text-to-speech failed: {e}")
            raise Exception(f"Failed to generate speech: {str(e)}")
    
    def text_to_speech_hd(self, text: str, voice: str = "alloy") -> bytes:
        """
        Convert text to speech using OpenAI TTS HD model (higher quality)
        Available voices: alloy, echo, fable, onyx, nova, shimmer
        Returns: audio bytes (MP3 format)
        """
        try:
            response = self.client.audio.speech.create(
                model="tts-1-hd",
                voice=voice,
                input=text
            )
            
            audio_content = response.content
            
            logger.info(f"Text-to-speech HD completed. Voice: {voice}")
            
            return audio_content
            
        except Exception as e:
            logger.error(f"Text-to-speech HD failed: {e}")
            raise Exception(f"Failed to generate speech: {str(e)}")

voice_service = VoiceService()
