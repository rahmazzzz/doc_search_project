import logging
from typing import Optional, Dict, Any, List

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


class LLMSearchService:
    """
    Service for answering user questions by:
    - Retrieving the appropriate prompt template
    - Performing semantic search for relevant chunks
    - Calling the selected LLM provider to generate a response
    - Storing and retrieving conversation history
    """

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
        file_id: Optional[str],
        prompt_name: str = "default",
        language: str = "english",
        provider_name: Optional[str] = None,
        chat_history: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        try:
            provider = (provider_name or settings.LLM_PROVIDER).lower()
            llm_client = LLMChatFactory.get_client(provider)

            # 1. Get prompt template
            try:
                prompt_doc = await self.prompt_repository.get_prompt_by_name(prompt_name) \
                             or (_ for _ in ()).throw(PromptNotFoundError(prompt_name))
            except PromptNotFoundError:
                raise
            except Exception as e:
                logger.exception("Error retrieving prompt")
                raise ContextRetrievalError(str(e))

            system_text = prompt_doc.get("system", "")
            user_template = prompt_doc.get("user", "{question}")

            # 2. Retrieve chat history or use provided
            try:
                history_source = chat_history or await self.mongo_repository.get_chat_history(user_id, provider)
                role_key_map = {
                    True: "content",
                    False: "message"
                }
                normalized_history = [
                    {"role": msg.get("role", "").lower(),
                     "content": msg.get(role_key_map["content" in msg], "")}
                    for msg in history_source
                ]
                chat_history = normalized_history
            except Exception as e:
                logger.exception("Error retrieving chat history")
                raise ChatHistoryRetrievalError(str(e))

            # 3. Retrieve context
            try:
                query_vector = self.cohere_embedding_client.embed([question])[0]
                results = self.qdrant_repository.search_vectors(
                    query_vector=query_vector,
                    file_id=file_id,
                    top_k=5
                )
                context = "\n".join(map(lambda hit: str(hit.payload.get("text", "")), results[:3])) if results else ""
            except Exception as e:
                logger.exception("Error retrieving context for question")
                raise ContextRetrievalError(str(e))

            # 4. Build user prompt
            final_user_prompt = user_template.format(
                question=question,
                context=context,
                language=language
            )

            # 5. Append user message
            chat_history.append({"role": "user", "content": final_user_prompt})

            # 6. Provider-specific message formatting (no if — use dict mapping)
            message_formatters = {
                "cohere": lambda history: [
                    {"role": {"user": "USER", "assistant": "CHATBOT"}.get(m["role"], "SYSTEM"),
                     "message": m["content"]}
                    for m in history
                ]
            }
            messages_for_llm = message_formatters.get(
                provider,
                lambda history: [{"role": m["role"], "content": m["content"]} for m in history]
            )(chat_history)

            # 7. Call LLM
            try:
                response_text = await llm_client.chat(
                    messages=messages_for_llm,
                    system=system_text,
                    documents=None
                )
            except Exception as e:
                logger.exception("Error calling LLM provider")
                raise LLMProviderError(provider, str(e))

            # 8. Append assistant message
            chat_history.append({"role": "assistant", "content": response_text})

            # 9. Save updated history
            try:
                await self.mongo_repository.save_chat_history(user_id, provider, chat_history)
            except Exception as e:
                logger.exception("Error saving chat history")
                raise ChatHistorySaveError(str(e))

            return {"answer": response_text}

        except Exception as e:
            logger.exception("Failed to answer question")
            return {"error": str(e)}
