from openai import OpenAI
from typing import List, Dict, Optional
from config import settings
import logging
from datetime import datetime, timezone

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
        Perform web search for legal information using OpenAI web search tool
        """
        try:
            logger.info(f"Performing web search for: {query}")

            # Use OpenAI's web search tool for fresh, web-grounded results.
            response = self.client.responses.create(
                model="gpt-4.1-mini",
                tools=[{"type": "web_search_preview"}],
                input=(
                    "You are a legal research assistant focused on Pakistani law. "
                    "Search the web and provide concise, factual findings with source-backed details. "
                    f"Return {max_results} most relevant and recent findings for: {query}"
                )
            )

            raw_response = response.model_dump() if hasattr(response, "model_dump") else response
            content = getattr(response, "output_text", None) or self._extract_output_text(raw_response)

            # Parse response + citations into structured results.
            web_results = self._parse_web_results(content, raw_response, max_results)
            
            logger.info(f"Found {len(web_results)} web search results")
            return web_results
            
        except Exception as e:
            logger.error(f"Web search failed: {e}")
            return []
    
    def _extract_output_text(self, raw_response: Dict) -> str:
        """
        Extract output text from a Responses API payload.
        """
        if not isinstance(raw_response, dict):
            return ""

        output_items = raw_response.get("output", [])
        text_parts = []

        for item in output_items:
            if item.get("type") != "message":
                continue
            for content in item.get("content", []):
                if content.get("type") == "output_text" and content.get("text"):
                    text_parts.append(content["text"])

        return "\n\n".join(text_parts).strip()

    def _extract_url_citations(self, raw_response: Dict) -> List[Dict]:
        """
        Extract URL citations from a Responses API payload.
        """
        citations = []

        if not isinstance(raw_response, dict):
            return citations

        output_items = raw_response.get("output", [])
        for item in output_items:
            if item.get("type") != "message":
                continue
            for content in item.get("content", []):
                if content.get("type") != "output_text":
                    continue
                for annotation in content.get("annotations", []):
                    if annotation.get("type") in {"url_citation", "web_citation"}:
                        citations.append(annotation)

        return citations

    def _parse_web_results(self, content: str, raw_response: Dict, max_results: int) -> List[Dict]:
        """
        Parse web search results into structured format
        """
        results = []

        retrieved_at = datetime.now(timezone.utc).isoformat()
        citations = self._extract_url_citations(raw_response)

        if citations:
            for idx, citation in enumerate(citations[:max_results], 1):
                source_url = citation.get("url") or ""
                source_title = citation.get("title") or "Web Search Result"
                published_date = citation.get("published_date") or citation.get("date")

                results.append({
                    "text": content.strip() if content else source_title,
                    "score": max(0.7, 0.98 - (idx * 0.08)),
                    "source": source_title,
                    "source_url": source_url,
                    "published_date": published_date,
                    "retrieved_at": retrieved_at,
                    "language": "english",
                    "chunk_index": idx,
                    "file_type": "web",
                    "province": "web_search",
                    "is_web_result": True
                })
            return results

        # Fallback when citations are unavailable: still preserve latest retrieval timestamp.
        if content and content.strip():
            sections = [s.strip() for s in content.split("\n\n") if s.strip()]
            for idx, section in enumerate(sections[:max_results], 1):
                results.append({
                    "text": section,
                    "score": max(0.7, 0.95 - (idx * 0.05)),
                    "source": "Web Search Result",
                    "source_url": None,
                    "published_date": None,
                    "retrieved_at": retrieved_at,
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
