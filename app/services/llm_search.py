# app/services/llm_search.py
import logging
from typing import Optional, List, Dict
from pydantic import BaseModel

from app.clients.llm_factory import LLMChatFactory
from app.core.config import settings
from app.clients.cohere_embedding_client import CohereEmbeddingClient
from app.repositories.qdrant_repository import QdrantRepository
from app.repositories.mongo_repository import MongoRepository
from app.repositories.prompt_repository import PromptRepository
from app.services.semantic_search import SemanticSearchService
from app.exceptions.llmsearch_exceptions import (
    PromptNotFoundError,
    ChatHistoryRetrievalError,
    ContextRetrievalError,
    LLMProviderError,
    ChatHistorySaveError
)

logger = logging.getLogger(__name__)

# --------------------- Pydantic Models ---------------------
class SearchResult(BaseModel):
    document_id: str
    text: str
    score: float = 0.0

class AnswerResponse(BaseModel):
    answer: str
    sources: List[SearchResult] = []

# --------------------- LLM Search Service ---------------------
class LLMSearchService:
    def __init__(
        self,
        semantic_search_service: SemanticSearchService,
        cohere_embedding_client: CohereEmbeddingClient,
        qdrant_repository: QdrantRepository,
        mongo_repository: MongoRepository,
        prompt_repository: PromptRepository,
    ):
        self.semantic_search_service = semantic_search_service
        self.cohere_embedding_client = cohere_embedding_client
        self.qdrant_repository = qdrant_repository
        self.mongo_repository = mongo_repository
        self.prompt_repository = prompt_repository

    async def answer_question(
        self,
        user_id: str,
        question: str,
        file_id: Optional[str] = None,
        prompt_name: str = "default",
        language: str = "english",
        provider_name: Optional[str] = None,
        chat_history: Optional[List[Dict[str, str]]] = None,
    ) -> AnswerResponse:
        try:
            provider = (provider_name or settings.LLM_PROVIDER).lower()
            print(f"Using LLM provider: {provider}")
            llm_client = LLMChatFactory.get_client(provider)
            print(f"LLM client initialized: {llm_client}")
            # --- 1. Get prompt template ---
            prompt_doc = await self.prompt_repository.get_prompt_by_name(prompt_name)
            if not prompt_doc:
                raise PromptNotFoundError(prompt_name)

            system_text = prompt_doc.get("system", "")
            user_template = prompt_doc.get("user", "{question}")

            # --- 2. Retrieve chat history ---
            history_source = chat_history or await self.mongo_repository.get_chat_history(user_id, provider)
            normalized_history = [
                {"role": msg.get("role", "").lower(), "content": str(msg.get("content", msg.get("message","")))}
                for msg in history_source
            ]
            chat_history = normalized_history

            # --- 3. Retrieve context from semantic search ---
            context_results: List[SearchResult] = []
            context_text = ""
            if file_id:
                search_hits = await self.semantic_search_service.search(question, username=user_id, file_id=file_id)
                for hit in search_hits:
                    text_value = hit.payload.get("text", "")
                    if not isinstance(text_value, str):
                        text_value = str(text_value)
                    context_results.append(
                        SearchResult(
                            document_id=str(hit.payload.get("id","")),
                            text=text_value,
                            score=getattr(hit, "score", 0.0)
                        )
                    )
                context_text = "\n".join([r.text for r in context_results[:3]])

            # --- 4. Build user prompt ---
            final_user_prompt = user_template.format(
                question=question,
                context=context_text,
                history=chat_history
            )
            chat_history.append({"role": "user", "content": final_user_prompt})

            # --- 6. Call LLM ---
            response = await llm_client.chat(
                user=final_user_prompt,
                system=system_text,
            )

            # --- 7. Append assistant message to history ---
            chat_history.append({"role": "assistant", "content": response.choices[0].message.parsed.answer})

            # --- 8. Save updated history ---
            await self.mongo_repository.save_chat_history(user_id, provider, chat_history)

            return AnswerResponse(answer=response.choices[0].message.parsed.answer, sources=context_results)

        except Exception as e:
            logger.exception("Failed to answer question")
            return AnswerResponse(answer=f"Error: {str(e)}", sources=[])
