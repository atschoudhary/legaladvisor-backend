from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from services.database_service import database_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class SettingsRequest(BaseModel):
    top_k: Optional[int] = None
    min_score: Optional[float] = None
    voice: Optional[str] = None
    tts_enabled: Optional[bool] = None

@router.get("/settings")
async def get_settings():
    """
    Get current admin settings from database
    
    Note: use_legal_search and province are automatically detected by the system
    and cannot be manually configured.
    """
    try:
        settings_data = database_service.get_settings()
        return {
            **settings_data,
            "note": "use_legal_search and province are auto-detected from query"
        }
    except Exception as e:
        logger.error(f"Failed to get settings: {e}")
        # Return defaults on error
        return {
            "top_k": 5,
            "min_score": 0.5,
            "voice": "alloy",
            "tts_enabled": False,
            "note": "use_legal_search and province are auto-detected from query"
        }

@router.post("/settings")
async def update_settings(settings_data: SettingsRequest):
    """
    Update admin settings in database
    
    **Available Settings (Admin Only)**:
    - **top_k** (int): Number of results (1-20) - Default: 5
    - **min_score** (float): Minimum relevance score (0.0-1.0) - Default: 0.5
    - **voice** (str): TTS voice (alloy, echo, fable, onyx, nova, shimmer) - Default: alloy
    - **tts_enabled** (bool): Enable audio responses - Default: false
    
    **Auto-Detected (Cannot be configured)**:
    - **use_legal_search**: Automatically enabled when legal keywords are detected
    - **province**: Automatically detected from query content
    """
    try:
        # Validate inputs
        if settings_data.top_k is not None:
            settings_data.top_k = max(1, min(20, settings_data.top_k))
        if settings_data.min_score is not None:
            settings_data.min_score = max(0.0, min(1.0, settings_data.min_score))
        if settings_data.voice is not None:
            valid_voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
            if settings_data.voice not in valid_voices:
                settings_data.voice = "alloy"
        
        # Update in database
        updated_settings = database_service.update_settings(
            top_k=settings_data.top_k,
            min_score=settings_data.min_score,
            voice=settings_data.voice,
            tts_enabled=settings_data.tts_enabled
        )
        
        logger.info(f"Admin settings updated: {updated_settings}")
        
        return {
            **updated_settings,
            "note": "use_legal_search and province are auto-detected from query"
        }
    except Exception as e:
        logger.error(f"Failed to update settings: {e}")
        # Return current settings on error
        return await get_settings()
