from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    # API Settings
    ENVIRONMENT: str = "production"
    API_VERSION: str = "v1"
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]
    
    # OpenAI
    OPENAI_API_KEY: str
    EMBEDDING_MODEL: str = "text-embedding-3-large"
    IMAGE_ANALYSIS_MODEL: str = "gpt-4.1"
    IMAGE_ANALYSIS_FALLBACK_MODEL: str = "gpt-4o"
    IMAGE_ANALYSIS_REFINER_MODEL: str = "gpt-4.1"
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_IMAGE_MODEL: str = "gemini-3-flash-preview"
    
    # Qdrant
    QDRANT_URL: str
    QDRANT_API_KEY: str
    
    # Database
    DB_HOST: str
    DB_PORT: int = 6438
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_SSLMODE: str = "require"
    
    # Admin
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin123"
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    # Collections
    COLLECTION_SINDH: str = "legaladvisor_sindh"
    COLLECTION_PUNJAB: str = "legaladvisor_punjab"
    COLLECTION_KPK: str = "legaladvisor_khyber_pakhtunkhwa"
    COLLECTION_BALOCHISTAN: str = "legaladvisor_balochistan"
    COLLECTION_ALL_PAKISTAN: str = "legaladvisor_all_pakistan"
    
    # Query Settings
    DEFAULT_TOP_K: int = 5
    MAX_TOP_K: int = 20
    MIN_SCORE_THRESHOLD: float = 0.5
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
