# app/services/tavily_service.py
from tavily import TavilyClient
from typing import List, Dict
import asyncio
import logging

logger = logging.getLogger(__name__)

class TavilyService:
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("TAVILY_API_KEY is missing in environment variables")
        self.client = TavilyClient(api_key=api_key)

    async def search(self, query: str, max_results: int = 5) -> List[Dict]:
        """Perform a web search and return structured results as a list of dicts"""
        if not query:
            logger.warning("Empty query passed to TavilyService.search")
            return []

        try:
            # Wrap synchronous SDK call in executor
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, lambda: self.client.search(query=query, max_results=max_results)
            )

            if not isinstance(response, dict):
                logger.warning(f"Unexpected Tavily response type: {type(response)}")
                return []

            results = response.get("results", [])
            if not isinstance(results, list):
                logger.warning("Tavily response 'results' is not a list")
                return []

            return results

        except Exception as e:
            logger.error(f"Tavily search failed: {e}")
            return []
