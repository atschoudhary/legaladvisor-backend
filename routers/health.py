from fastapi import APIRouter, HTTPException
from models import HealthResponse
from services.qdrant_service import qdrant_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    Returns API status and collection information
    """
    try:
        info = qdrant_service.get_collections_info()
        
        return HealthResponse(
            status="healthy",
            version="1.0.0",
            collections_available=info["collections"],
            total_chunks=info["total_chunks"]
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")
