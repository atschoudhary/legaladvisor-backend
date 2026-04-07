from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from routers import health, unified
from config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="LegalAdvisor API",
    description="Unified Multilingual Legal Assistant API",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(unified.router, prefix="/api/v1", tags=["unified"])

# Serve test UI at root
@app.get("/")
async def root():
    """Serve test UI"""
    return FileResponse("static/index.html")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
async def startup_event():
    logger.info("=" * 60)
    logger.info("LegalAdvisor API v2.0 - Unified Endpoint")
    logger.info("=" * 60)
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info("")
    logger.info("Available Endpoints:")
    logger.info("  - POST /api/v1/message  - Send message with optional preferences")
    logger.info("  - GET  /api/v1/health   - Health check")
    logger.info("")
    logger.info("Web UI: http://localhost:8000")
    logger.info("API Docs: http://localhost:8000/docs")
    logger.info("=" * 60)
    logger.info("  - GET  /api/v1/health         - Health check")
    logger.info("")
    logger.info("Web UI: http://localhost:8000")
    logger.info("API Docs: http://localhost:8000/docs")
    logger.info("=" * 60)

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("LegalAdvisor API shutting down...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        reload=settings.ENVIRONMENT == "development"
    )
