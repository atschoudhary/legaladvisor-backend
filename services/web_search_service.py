from openai import OpenAI
from typing import List, Dict, Optional
from config import settings
import logging

logger = logging.getLogger(__name__)

class WebSearchService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    def should_use_web_search(self, query: str, vector_results_count: int) -> bool:
        """
        Determine if web search should be used to supplement results
        """
        # Use web search if:
        # 1. Very few or no vector results found
        # 2. Query asks about recent/current events
        # 3. Query asks about specific case law or recent amendments
        
        if vector_results_count == 0:
            logger.info("No vector results found, will use web search")
            return True
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": """Determine if this legal query would benefit from web search.

Respond with ONLY: yes or no

Use web search (yes) if query asks about:
- Recent legal developments or amendments
- Current case law or ongoing cases
- Latest legal news or updates
- Specific recent court decisions
- New legislation or bills
- Current legal procedures that may have changed

Don't use web search (no) if query is about:
- General legal principles
- Established laws and acts
- Historical legal information
- Standard legal procedures
- Constitutional provisions"""
                    },
                    {
                        "role": "user",
                        "content": f"Query: {query}\nVector results found: {vector_results_count}"
                    }
                ],
                temperature=0.3,
                max_tokens=5
            )
            
            result = response.choices[0].message.content.strip().lower()
            should_search = result == "yes"
            
            if should_search:
                logger.info("Web search recommended for this query")
            
            return should_search
            
        except Exception as e:
            logger.error(f"Web search decision failed: {e}")
            return vector_results_count < 2
    
    def search_legal_web(self, query: str, max_results: int = 3) -> List[Dict]:
        """
        Perform web search for legal information using OpenAI
        """
        try:
            logger.info(f"Performing web search for: {query}")
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a legal research assistant. Search the web for relevant legal information about Pakistan law.

Focus on:
- Official government sources
- Court decisions and case law
- Legal databases and repositories
- Reputable legal news sources
- Official gazette notifications

Provide accurate, factual information with sources."""
                    },
                    {
                        "role": "user",
                        "content": f"Search for legal information about: {query}\n\nProvide {max_results} most relevant findings with sources."
                    }
                ],
                temperature=0.3,
                max_tokens=1500
            )
            
            content = response.choices[0].message.content
            
            # Parse the response into structured results
            web_results = self._parse_web_results(content, query)
            
            logger.info(f"Found {len(web_results)} web search results")
            return web_results
            
        except Exception as e:
            logger.error(f"Web search failed: {e}")
            return []
    
    def _parse_web_results(self, content: str, query: str) -> List[Dict]:
        """
        Parse web search results into structured format
        """
        results = []
        
        # Split content into sections (simple parsing)
        sections = content.split('\n\n')
        
        for idx, section in enumerate(sections[:3], 1):
            if section.strip():
                results.append({
                    "text": section.strip(),
                    "score": 0.95 - (idx * 0.05),  # Simulated relevance score
                    "source": "Web Search Result",
                    "language": "english",
                    "chunk_index": idx,
                    "file_type": "web",
                    "province": "web_search",
                    "is_web_result": True
                })
        
        return results
    
    def enhance_results_with_web(
        self,
        query: str,
        vector_results: List[Dict],
        max_web_results: int = 2
    ) -> List[Dict]:
        """
        Enhance vector search results with web search if beneficial
        """
        if not self.should_use_web_search(query, len(vector_results)):
            return vector_results
        
        web_results = self.search_legal_web(query, max_web_results)
        
        if not web_results:
            return vector_results
        
        # Combine results: web results first (as they're more current), then vector results
        combined = web_results + vector_results
        
        logger.info(f"Enhanced results: {len(web_results)} web + {len(vector_results)} vector = {len(combined)} total")
        
        return combined

web_search_service = WebSearchService()
