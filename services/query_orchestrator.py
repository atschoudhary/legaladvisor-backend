from openai import OpenAI
from typing import Optional, List
from config import settings
import logging

logger = logging.getLogger(__name__)

class QueryOrchestrator:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        self.province_keywords = {
            "sindh": ["sindh", "karachi", "hyderabad", "sukkur", "larkana", "mirpurkhas"],
            "punjab": ["punjab", "lahore", "faisalabad", "rawalpindi", "multan", "gujranwala", "sialkot"],
            "khyber_pakhtunkhwa": ["kpk", "khyber pakhtunkhwa", "peshawar", "mardan", "abbottabad", "swat"],
            "balochistan": ["balochistan", "quetta", "gwadar", "turbat", "khuzdar"]
        }
    
    def determine_province(self, query: str, user_province: Optional[str] = None) -> str:
        """
        Intelligently determine which province collection to search based on query content
        Returns: province name or None (for all collections)
        """
        # If user explicitly specified province, use it
        if user_province:
            logger.info(f"Using user-specified province: {user_province}")
            return user_province
        
        # Check for province keywords in query
        query_lower = query.lower()
        for province, keywords in self.province_keywords.items():
            for keyword in keywords:
                if keyword in query_lower:
                    logger.info(f"Detected province from keywords: {province}")
                    return province
        
        # Use AI to determine if query is province-specific
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a legal query analyzer for Pakistan. Determine if this query is specific to a particular province or should search all collections.

Respond with ONLY ONE of these:
- sindh (if specifically about Sindh province)
- punjab (if specifically about Punjab province)
- khyber_pakhtunkhwa (if specifically about KPK)
- balochistan (if specifically about Balochistan)
- all (if general query or should search all collections)

Default to "all" unless the query CLEARLY indicates a specific province.

Examples:
- "Punjab police arrest" → punjab
- "Karachi laws" → sindh
- "criminal procedure" → all
- "constitution rights" → all
- "property laws" → all"""
                    },
                    {
                        "role": "user",
                        "content": f"Query: {query}"
                    }
                ],
                temperature=0.3,
                max_tokens=20
            )
            
            province = response.choices[0].message.content.strip().lower()
            
            # Validate response
            valid_provinces = ["sindh", "punjab", "khyber_pakhtunkhwa", "balochistan", "all"]
            if province in valid_provinces:
                if province == "all":
                    logger.info(f"AI determined: search all collections")
                    return None  # None means search all
                else:
                    logger.info(f"AI determined province: {province}")
                    return province
            else:
                logger.warning(f"Invalid AI response: {province}, defaulting to all collections")
                return None
                
        except Exception as e:
            logger.error(f"Province determination failed: {e}")
            return None
    
    def should_search_multiple_collections(self, query: str, determined_province: Optional[str]) -> bool:
        """
        Determine if query should search across multiple collections
        """
        # If no specific province determined, search all
        if determined_province is None:
            return True
        
        # If specific province determined, check if comparative query
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": """Determine if this legal query requires comparing across provinces.

Respond with ONLY: yes or no

Search multiple (yes) if:
- Query explicitly compares provinces
- Query asks about "all provinces" or "nationwide"
- Query asks "which province" or "where"

Search single (no) if:
- Query is about specific province only
- Query doesn't require comparison"""
                    },
                    {
                        "role": "user",
                        "content": f"Query: {query}"
                    }
                ],
                temperature=0.3,
                max_tokens=5
            )
            
            result = response.choices[0].message.content.strip().lower()
            return result == "yes"
            
        except Exception as e:
            logger.error(f"Multi-collection check failed: {e}")
            return False
    
    def get_search_strategy(self, query: str, user_province: Optional[str] = None) -> dict:
        """
        Get complete search strategy for the query
        Returns: {
            "primary_province": str or None,
            "search_multiple": bool,
            "provinces_to_search": List[str],
            "reasoning": str
        }
        """
        determined_province = self.determine_province(query, user_province)
        search_multiple = self.should_search_multiple_collections(query, determined_province)
        
        # Default: search all collections
        if determined_province is None:
            provinces_to_search = ["sindh", "punjab", "khyber_pakhtunkhwa", "balochistan", "all_pakistan"]
            reasoning = "Searching all collections for comprehensive results"
            primary_province = "all_pakistan"
        elif search_multiple:
            provinces_to_search = ["sindh", "punjab", "khyber_pakhtunkhwa", "balochistan", "all_pakistan"]
            reasoning = f"Comparative query - searching all collections with focus on {determined_province}"
            primary_province = determined_province
        else:
            provinces_to_search = [determined_province]
            reasoning = f"Query is specific to {determined_province}"
            primary_province = determined_province
        
        strategy = {
            "primary_province": primary_province,
            "search_multiple": len(provinces_to_search) > 1,
            "provinces_to_search": provinces_to_search,
            "reasoning": reasoning
        }
        
        logger.info(f"Search strategy: {strategy}")
        return strategy

query_orchestrator = QueryOrchestrator()
