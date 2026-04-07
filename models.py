from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

class Province(str, Enum):
    SINDH = "sindh"
    PUNJAB = "punjab"
    KPK = "khyber_pakhtunkhwa"
    BALOCHISTAN = "balochistan"
    ALL_PAKISTAN = "all_pakistan"

class Language(str, Enum):
    ENGLISH = "english"
    URDU = "urdu"
    PUNJABI = "punjabi"
    SINDHI = "sindhi"

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000, description="Legal query text")
    province: Optional[Province] = Field(None, description="Filter by province")
    language: Optional[Language] = Field(None, description="Filter by language")
    top_k: Optional[int] = Field(5, ge=1, le=20, description="Number of results to return")
    min_score: Optional[float] = Field(0.5, ge=0.0, le=1.0, description="Minimum relevance score")

class SearchResult(BaseModel):
    text: str
    score: float
    source: str
    language: str
    chunk_index: int
    file_type: str
    province: Optional[str] = None
    is_web_result: Optional[bool] = False

class QueryResponse(BaseModel):
    query: str
    synthesized_answer: Optional[str] = None
    results: List[SearchResult]
    total_results: int
    province_filter: Optional[str] = None
    language_filter: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    version: str
    collections_available: List[str]
    total_chunks: int
