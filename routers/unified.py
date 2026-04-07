from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse, Response
from typing import Optional
from services.multilingual_chat_service import multilingual_chat_service
from services.document_reader_service import document_reader_service
from services.voice_service import voice_service
from services.image_understanding_service import image_understanding_service
from services.embedding_service import embedding_service
from services.qdrant_service import qdrant_service
from services.query_orchestrator import query_orchestrator
from services.web_search_service import web_search_service
from services.answer_synthesis_service import answer_synthesis_service
from services.translation_service import translation_service
from services.database_service import database_service
import logging
import base64

logger = logging.getLogger(__name__)
router = APIRouter()

async def detect_legal_query(message: str, has_document: bool) -> bool:
    """
    Use LLM to intelligently detect if the query is legal-related
    """
    # If document is attached, likely legal
    if has_document:
        return True
    
    try:
        # Use OpenAI to intelligently detect legal queries
        from services.multilingual_chat_service import multilingual_chat_service
        
        response = multilingual_chat_service.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """You are a legal query classifier for Pakistani law.

Analyze the user's query and determine if it is related to legal matters, laws, rights, or legal procedures.

Legal queries include:
- Questions about laws, rights, legal procedures
- Questions about courts, judges, lawyers, police
- Questions about contracts, property, marriage, divorce, inheritance
- Questions about crimes, punishments, arrests, bail
- Questions about constitution, legislation, regulations
- Questions about legal age, legal requirements, legal validity
- Any query seeking legal information or guidance

Non-legal queries include:
- General greetings and casual conversation
- Questions about weather, food, travel, entertainment
- Technical questions unrelated to law
- General knowledge questions not about law
- Personal advice not related to legal matters

Respond with ONLY "yes" if the query is legal-related, or "no" if it is not.
Do not provide any explanation, just "yes" or "no"."""
                },
                {
                    "role": "user",
                    "content": message
                }
            ],
            temperature=0.1,
            max_tokens=5
        )
        
        result = response.choices[0].message.content.strip().lower()
        is_legal = result == "yes"
        
        logger.info(f"LLM legal query detection: '{message[:50]}...' -> {is_legal}")
        return is_legal
        
    except Exception as e:
        logger.error(f"LLM legal detection failed: {e}, falling back to keyword detection")
        
        # Fallback to keyword detection if LLM fails
        legal_keywords = [
            'law', 'legal', 'court', 'judge', 'lawyer', 'attorney', 'constitution',
            'rights', 'act', 'section', 'article', 'criminal', 'civil', 'case',
            'justice', 'police', 'arrest', 'bail', 'property', 'contract', 'marriage',
            'divorce', 'inheritance', 'will', 'testament', 'crime', 'punishment',
            'qanoon', 'adalat', 'wakeel', 'haq', 'huqooq', 'shaadi', 'talaq'
        ]
        
        message_lower = message.lower()
        for keyword in legal_keywords:
            if keyword in message_lower:
                return True
        
        return False

@router.post("/message")
async def unified_message(
    message: str = Form(...),
    image: Optional[UploadFile] = File(None),
    document: Optional[UploadFile] = File(None),
    audio: Optional[UploadFile] = File(None)
):
    """
    Unified endpoint for all interactions - Fully Automatic
    
    **Required:**
    - **message**: Text message/query (or empty if audio provided)
    
    **Optional Files:**
    - **image**: Image file for analysis
    - **document**: Document file (PDF, DOCX, TXT) for analysis
    - **audio**: Audio file (will be transcribed)
    
    **Automatic Features:**
    - Language detection from query
    - Legal search enabled automatically using LLM-based intelligent detection
    - Province detection from query content
    - Context integration from images/documents
    - TTS audio generation (if enabled in settings)
    
    **Examples:**
    1. "What is property law?" → Auto-detects legal query, enables search
    2. "Hello, how are you?" → Regular chat, no legal search
    3. "Punjab police procedure" → Auto-detects Punjab + legal query
    4. Image + "Explain this" → Analyzes image, detects if legal
    
    Returns unified response with answer in user's language
    """
    try:
        context_parts = []
        final_message = message
        detected_language = None
        
        # 1. Process Audio (if provided) - transcribe and use as message
        if audio:
            logger.info(f"Processing audio: {audio.filename}")
            audio_content = await audio.read()
            transcription = voice_service.speech_to_text(audio_content, audio.filename)
            final_message = transcription["text"]
            if not detected_language:
                detected_language = transcription.get("language", "english")
            context_parts.append(f"[Audio transcription: {final_message}]")
        
        # 2. Automatically detect if this is a legal query
        use_legal_search = await detect_legal_query(final_message, document is not None)
        logger.info(f"Legal query detected: {use_legal_search}")
        
        # Get admin-configured settings from database
        admin_settings = database_service.get_settings()
        top_k = admin_settings.get("top_k", 5)
        min_score = admin_settings.get("min_score", 0.5)
        province = None  # Will be auto-detected by query_orchestrator
        
        # 3. Process Image (if provided)
        if image:
            logger.info(f"Processing image: {image.filename}")
            image_content = await image.read()
            
            # Extract text from image if it contains text
            try:
                image_text = image_understanding_service.extract_text_from_image(image_content)
                if image_text and len(image_text.strip()) > 10:
                    context_parts.append(f"[Text from image: {image_text}]")
            except:
                pass
            
            # Analyze image with user's query
            image_analysis = image_understanding_service.analyze_image(
                image_content,
                final_message,
                detected_language or "english"
            )
            context_parts.append(f"[Image analysis: {image_analysis}]")
        
        # 3. Process Document (if provided)
        if document:
            logger.info(f"Processing document: {document.filename}")
            doc_content = await document.read()
            doc_text = document_reader_service.extract_text(doc_content, document.filename)
            
            # Analyze document with user's query
            doc_analysis = document_reader_service.analyze_document(
                doc_text,
                final_message,
                detected_language or "english"
            )
            context_parts.append(f"[Document analysis: {doc_analysis}]")
        
        # 4. Legal Document Search (if enabled)
        legal_results = None
        if use_legal_search:
            logger.info("Performing legal document search")
            
            # Translate query if needed
            translated_query, lang = translation_service.detect_and_translate_query(final_message)
            if not detected_language:
                detected_language = lang
            
            # Get search strategy
            search_strategy = query_orchestrator.get_search_strategy(translated_query, province)
            
            # Generate embedding
            query_vector = embedding_service.generate_embedding(translated_query)
            
            # Search
            all_results = []
            if search_strategy["search_multiple"]:
                for prov in search_strategy["provinces_to_search"]:
                    try:
                        results = qdrant_service.search(
                            query_vector=query_vector,
                            province=prov,
                            language=None,
                            top_k=top_k,
                            min_score=min_score
                        )
                        all_results.extend(results)
                    except Exception as e:
                        logger.warning(f"Search failed for {prov}: {e}")
                all_results.sort(key=lambda x: x["score"], reverse=True)
                all_results = all_results[:top_k]
            else:
                all_results = qdrant_service.search(
                    query_vector=query_vector,
                    province=search_strategy["primary_province"],
                    language=None,
                    top_k=top_k,
                    min_score=min_score
                )
            
            # Enhance with web search
            all_results = web_search_service.enhance_results_with_web(
                translated_query,
                all_results,
                max_web_results=2
            )
            
            legal_results = all_results
            
            # Add legal context
            if all_results:
                legal_context = "\n".join([f"- {r['text'][:200]}..." for r in all_results[:3]])
                context_parts.append(f"[Legal documents found: {legal_context}]")
        
        # 5. Generate Final Response
        if legal_results:
            # Use answer synthesis for legal queries
            synthesis_result = answer_synthesis_service.synthesize_answer(
                final_message,
                legal_results,
                detected_language or "english"
            )
            final_response = synthesis_result.get("answer")
        else:
            # Use chat for general queries with context
            if context_parts:
                enhanced_message = f"{final_message}\n\nContext:\n" + "\n".join(context_parts)
            else:
                enhanced_message = final_message
            
            chat_result = multilingual_chat_service.chat(enhanced_message)
            final_response = chat_result["response"]
            if not detected_language:
                detected_language = chat_result["language"]
        
        # 6. Generate TTS Audio (if enabled)
        audio_base64 = None
        if admin_settings.get("tts_enabled", False):
            try:
                logger.info("Generating TTS audio")
                voice = admin_settings.get("voice", "alloy")
                audio_bytes = voice_service.text_to_speech(final_response, voice)
                audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
                logger.info("TTS audio generated successfully")
            except Exception as e:
                logger.error(f"TTS generation failed: {e}")
                # Continue without audio
        
        # 7. Return Unified Response
        response_data = {
            "success": True,
            "message": final_message,
            "response": final_response,
            "language": detected_language,
            "context": {
                "had_audio": audio is not None,
                "had_image": image is not None,
                "had_document": document is not None,
                "used_legal_search": use_legal_search,
                "legal_results_count": len(legal_results) if legal_results else 0,
                "auto_detected": True  # Indicates automatic detection
            }
        }
        
        # Add audio if TTS was enabled
        if audio_base64:
            response_data["audio"] = audio_base64
        
        return JSONResponse(content=response_data)
        
    except Exception as e:
        logger.error(f"Unified message processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
