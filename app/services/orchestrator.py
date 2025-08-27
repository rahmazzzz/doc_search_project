# app/services/orchestrator.py
from typing import Dict, Optional, List
from app.services.semantic_search import SemanticSearchService
from app.services.llm_search import LLMSearchService
import logging

logger = logging.getLogger(__name__)

class OrchestratorAgent:
    def __init__(self, doc_service: SemanticSearchService, web_service: LLMSearchService, llm_client):
        self.doc_service = doc_service
        self.web_service = web_service
        self.llm_client = llm_client

    async def answer(
        self, 
        query: str, 
        username: Optional[str] = None, 
        file_id: Optional[str] = None
    ) -> Dict:
        steps = ["Received query"]

        # Step 1: search in documents (if file_id is provided)
        doc_result: List[dict] = []
        if file_id:
            doc_result = await self.doc_service.search(query, username=username, file_id=file_id)
        steps.append("Searched documents")

        # Step 2: search on web (Tavily)
        web_result: List[dict] = await self.web_service.search(query)
        steps.append("Searched web (Tavily)")

        # Step 3: generate final answer with LLM
        decision_prompt = f"""
        You are an expert assistant helping to answer the user's query.

        User query: {query}

        Document search results: {doc_result}
        Web search results: {web_result}

        Compose a clear final answer using the best information available.
        """
        try:
            raw_response = await self.llm_client.chat(
                user=decision_prompt,
                system="You are a helpful assistant."
            )
        except Exception as e:
            logger.error(f"LLM failed: {e}")
            return {
                "final_answer": "",
                "decision": "error",
                "sources": [],
                "steps": steps + ["Error occurred during orchestration"]
            }

        # Extract final answer from LLM response
        final_answer = getattr(raw_response, "answer", str(raw_response))
        sources = getattr(raw_response, "sources", [])

        steps.append("Mistral decided best source")

        # Step 4: compute decision based on available results
        if doc_result and not web_result:
            decision = "document"
        elif web_result and not doc_result:
            decision = "web"
        elif doc_result and web_result:
            decision = "both"
        else:
            decision = "unknown"

        return {
            "final_answer": final_answer,
            "decision": decision,
            "sources": sources,
            "steps": steps
        }
