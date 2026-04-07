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
