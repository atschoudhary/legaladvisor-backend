from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from typing import List, Optional, Dict
from config import settings
import logging

logger = logging.getLogger(__name__)

class QdrantService:
    def __init__(self):
        self.client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY
        )
        self.collection_map = {
            "sindh": settings.COLLECTION_SINDH,
            "punjab": settings.COLLECTION_PUNJAB,
            "khyber_pakhtunkhwa": settings.COLLECTION_KPK,
            "balochistan": settings.COLLECTION_BALOCHISTAN,
            "all_pakistan": settings.COLLECTION_ALL_PAKISTAN
        }
    
    def get_collection_name(self, province: Optional[str]) -> str:
        """Get collection name based on province"""
        if province and province in self.collection_map:
            return self.collection_map[province]
        return settings.COLLECTION_ALL_PAKISTAN
    
    def search(
        self,
        query_vector: List[float],
        province: Optional[str] = None,
        language: Optional[str] = None,
        top_k: int = 5,
        min_score: float = 0.5
    ) -> List[Dict]:
        """
        Search for relevant legal chunks
        """
        collection_name = self.get_collection_name(province)
        
        # Build filter - only if language is specified
        search_filter = None
        if language:
            search_filter = Filter(
                must=[
                    FieldCondition(
                        key="language",
                        match=MatchValue(value=language)
                    )
                ]
            )
        
        try:
            results = self.client.query_points(
                collection_name=collection_name,
                query=query_vector,
                query_filter=search_filter,
                limit=top_k,
                score_threshold=min_score,
                with_payload=True
            ).points
            
            return [
                {
                    "text": result.payload.get("text"),
                    "score": result.score,
                    "source": result.payload.get("source"),
                    "language": result.payload.get("language"),
                    "chunk_index": result.payload.get("chunk_index"),
                    "file_type": result.payload.get("file_type"),
                    "province": province or "all_pakistan"
                }
                for result in results
            ]
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise
    
    def get_collections_info(self) -> Dict:
        """Get information about all collections"""
        try:
            collections = self.client.get_collections().collections
            total_chunks = 0
            available_collections = []
            
            for col in collections:
                if col.name.startswith("legaladvisor_"):
                    info = self.client.get_collection(col.name)
                    total_chunks += info.points_count
                    available_collections.append(col.name)
            
            return {
                "collections": available_collections,
                "total_chunks": total_chunks
            }
        except Exception as e:
            logger.error(f"Failed to get collections info: {e}")
            raise

qdrant_service = QdrantService()
