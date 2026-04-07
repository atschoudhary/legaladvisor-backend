from openai import OpenAI
from config import settings
import logging
import PyPDF2
import docx
import io

logger = logging.getLogger(__name__)

class DocumentReaderService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    def extract_text_from_pdf(self, file_content: bytes) -> str:
        """Extract text from PDF file"""
        try:
            pdf_file = io.BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"PDF extraction failed: {e}")
            raise Exception(f"Failed to extract text from PDF: {str(e)}")
    
    def extract_text_from_docx(self, file_content: bytes) -> str:
        """Extract text from DOCX file"""
        try:
            doc_file = io.BytesIO(file_content)
            doc = docx.Document(doc_file)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text.strip()
        except Exception as e:
            logger.error(f"DOCX extraction failed: {e}")
            raise Exception(f"Failed to extract text from DOCX: {str(e)}")
    
    def extract_text_from_txt(self, file_content: bytes) -> str:
        """Extract text from TXT file"""
        try:
            return file_content.decode('utf-8').strip()
        except Exception as e:
            logger.error(f"TXT extraction failed: {e}")
            raise Exception(f"Failed to extract text from TXT: {str(e)}")
    
    def extract_text(self, file_content: bytes, filename: str) -> str:
        """Extract text based on file type"""
        if filename.lower().endswith('.pdf'):
            return self.extract_text_from_pdf(file_content)
        elif filename.lower().endswith('.docx'):
            return self.extract_text_from_docx(file_content)
        elif filename.lower().endswith('.txt'):
            return self.extract_text_from_txt(file_content)
        else:
            raise Exception(f"Unsupported file type: {filename}")
    
    def analyze_document(self, document_text: str, user_query: str, language: str = "english") -> str:
        """
        Analyze document and provide simplified explanation
        """
        try:
            language_names = {
                "english": "English",
                "urdu": "Urdu",
                "punjabi": "Pakistani Punjabi (Shahmukhi script)",
                "sindhi": "Sindhi",
                "roman_urdu": "Roman Urdu (Urdu written in English alphabet)"
            }
            
            target_language = language_names.get(language, "English")
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": f"""You are a legal document analyzer for Pakistani law.

Analyze the provided document and answer the user's question in {target_language}.

RULES:
1. Provide clear, simplified explanations
2. Use markdown formatting for better readability
3. Respond in {target_language}
4. Focus on the most relevant information
5. If the document is legal, maintain accuracy of legal terms
6. Break down complex concepts into simple points

MARKDOWN FORMATTING:
- Use **bold** for important terms
- Use ## for main sections
- Use - for bullet points
- Use numbered lists for steps"""
                    },
                    {
                        "role": "user",
                        "content": f"""Document Content:
{document_text[:8000]}

User Question: {user_query}

Please analyze this document and answer the question."""
                    }
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            answer = response.choices[0].message.content
            logger.info(f"Document analyzed successfully in {language}")
            return answer
            
        except Exception as e:
            logger.error(f"Document analysis failed: {e}")
            raise Exception(f"Failed to analyze document: {str(e)}")

document_reader_service = DocumentReaderService()
