from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from routers import health, unified, settings, audio, admin
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
app.include_router(settings.router, prefix="/api/v1", tags=["settings"])
app.include_router(audio.router, prefix="/api/v1", tags=["audio"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])

# Leapcell healthcheck endpoint
@app.get("/kaithhealthcheck")
async def leapcell_healthcheck():
    """Leapcell platform healthcheck"""
    return {"status": "ok"}

# Serve test UI at root
@app.get("/")
async def root():
    """Serve test UI"""
    return FileResponse("static/index.html")

# Serve admin panel
@app.get("/admin.html")
async def admin_panel():
    """Serve admin panel"""
    return FileResponse("static/admin.html")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
async def startup_event():
    # Initialize database
    from services.database_service import database_service
    try:
        database_service.init_tables()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
    
    logger.info("=" * 60)
    logger.info("LegalAdvisor API v2.0 - Unified Endpoint")
    logger.info("=" * 60)
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info("")
    logger.info("Available Endpoints:")
    logger.info("  - POST /api/v1/message  - Send message with optional preferences")
    logger.info("  - POST /api/v1/audio    - Audio-only mode (audio in, audio out)")
    logger.info("  - GET  /api/v1/health   - Health check")
    logger.info("  - GET  /api/v1/settings - Get settings")
    logger.info("  - POST /api/v1/settings - Update settings")
    logger.info("  - POST /api/v1/admin/login - Admin login")
    logger.info("  - GET  /api/v1/admin/settings - Get admin settings (auth required)")
    logger.info("  - POST /api/v1/admin/settings - Update admin settings (auth required)")
    logger.info("  - GET  /kaithhealthcheck - Leapcell healthcheck")
    logger.info("")
    logger.info("Web UI: http://localhost:8080")
    logger.info("API Docs: http://localhost:8080/docs")
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
