from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import Response
from services.multilingual_chat_service import multilingual_chat_service
from services.voice_service import voice_service
from services.embedding_service import embedding_service
from services.qdrant_service import qdrant_service
from services.query_orchestrator import query_orchestrator
from services.web_search_service import web_search_service
from services.answer_synthesis_service import answer_synthesis_service
from services.translation_service import translation_service
from services.database_service import database_service
import logging

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

@router.post("/audio")
async def audio_mode(
    audio: UploadFile = File(...)
):
    """
    Audio-only endpoint for voice conversations
    
    **Input**: Audio file only
    **Output**: Audio response only (MP3)
    
    **Flow**:
    1. Transcribe audio to text (Speech-to-Text)
    2. Detect if legal query using LLM
    3. Process query and generate text response
    4. Convert text response to audio (Text-to-Speech)
    5. Return audio file directly
    
    **Supported Audio Formats**: MP3, MP4, MPEG, MPGA, M4A, WAV, WebM
    
    **Example**:
    ```bash
    curl -X POST http://localhost:8080/api/v1/audio \
      -F "audio=@question.mp3" \
      -o response.mp3
    ```
    
    Returns: MP3 audio file
    """
    try:
        logger.info(f"Audio mode: Processing audio file: {audio.filename}")
        
        # 1. Transcribe audio to text
        audio_content = await audio.read()
        transcription = voice_service.speech_to_text(audio_content, audio.filename)
        message = transcription["text"]
        detected_language = transcription.get("language", "english")
        
        logger.info(f"Audio transcribed: '{message[:100]}...'")
        
        # 2. Detect if legal query
        use_legal_search = await detect_legal_query(message, False)
        logger.info(f"Legal query detected: {use_legal_search}")
        
        # Get admin settings from database
        admin_settings = database_service.get_settings()
        top_k = admin_settings.get("top_k", 5)
        min_score = admin_settings.get("min_score", 0.5)
        province = None
        
        # 3. Process query
        legal_results = None
        if use_legal_search:
            logger.info("Performing legal document search")
            
            # Translate query if needed
            translated_query, lang = translation_service.detect_and_translate_query(message)
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
        
        # 4. Generate text response
        if legal_results:
            synthesis_result = answer_synthesis_service.synthesize_answer(
                message,
                legal_results,
                detected_language or "english"
            )
            text_response = synthesis_result.get("answer")
        else:
            chat_result = multilingual_chat_service.chat(message)
            text_response = chat_result["response"]
            if not detected_language:
                detected_language = chat_result["language"]
        
        logger.info(f"Text response generated: '{text_response[:100]}...'")
        
        # 5. Convert text response to audio
        voice = admin_settings.get("voice", "alloy")
        audio_bytes = voice_service.text_to_speech(text_response, voice)
        
        logger.info(f"Audio response generated successfully ({len(audio_bytes)} bytes)")
        
        # 6. Return audio file directly
        return Response(
            content=audio_bytes,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "attachment; filename=response.mp3"
            }
        )
        
    except Exception as e:
        logger.error(f"Audio mode processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
