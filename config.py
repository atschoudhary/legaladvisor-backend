from pydantic_settings import BaseSettings
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # API Settings
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "production")
    API_VERSION: str = "v1"
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]
    
    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-large")
    
    # Qdrant
    QDRANT_URL: str = os.getenv("QDRANT_URL")
    QDRANT_API_KEY: str = os.getenv("QDRANT_API_KEY")
    
    # Database
    DB_HOST: str = os.getenv("DB_HOST")
    DB_PORT: int = int(os.getenv("DB_PORT", "6438"))
    DB_NAME: str = os.getenv("DB_NAME")
    DB_USER: str = os.getenv("DB_USER")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD")
    DB_SSLMODE: str = os.getenv("DB_SSLMODE", "require")
    
    # Admin
    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "admin123")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
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
