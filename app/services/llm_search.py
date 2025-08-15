import logging
from typing import Optional, Dict, Any, List

from app.clients.llm_factory import LLMChatFactory
from app.core.config import settings
from app.clients.cohere_embedding_client import CohereEmbeddingClient
from app.repositories.qdrant_repository import QdrantRepository
from app.repositories.mongo_repository import MongoRepository
from app.repositories.prompt_repository import PromptRepository
from app.services.semantic_search import SemanticSearchService

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
        """
        Answer a question using the specified LLM provider, maintaining conversation history.
        Supports multi-turn chat by passing accumulated history to the LLM.
        """
        try:
            provider = (provider_name or settings.LLM_PROVIDER).lower()
            llm_client = LLMChatFactory.get_client(provider)

            # 1. Get prompt template
            prompt_doc = await self.prompt_repository.get_prompt_by_name(prompt_name)
            if not prompt_doc:
                return {"error": f"No prompt found with name '{prompt_name}'"}

            system_text = prompt_doc.get("system", "")
            user_template = prompt_doc.get("user", "{question}")

            # 2. Retrieve or use provided chat history
            if chat_history is None:
                chat_history = await self.mongo_repository.get_chat_history(user_id, provider)

            # ✅ Normalize history to always have lowercase role + "content"
            normalized_history = []
            for msg in chat_history:
                role = msg.get("role", "").lower()
                if "content" in msg:
                    normalized_history.append({"role": role, "content": msg["content"]})
                elif "message" in msg:  # Cohere old format
                    normalized_history.append({"role": role, "content": msg["message"]})
                else:
                    normalized_history.append({"role": role, "content": ""})
            chat_history = normalized_history

            # 3. Retrieve relevant context
            embedding = self.cohere_embedding_client.embed([question])
            query_vector = embedding[0]
            results = self.qdrant_repository.search_vectors(
                query_vector=query_vector,
                file_id=file_id,
                top_k=5
            )

            context_chunks = [str(hit.payload.get("text", "")) for hit in results[:3]] if results else []
            context = "\n".join(context_chunks)

            # 4. Build user prompt for this turn
            final_user_prompt = user_template.format(
                question=question,
                context=context,
                language=language
            )

            # 5. Append user message
            chat_history.append({"role": "user", "content": final_user_prompt})

            # 6. Convert chat history to provider-specific format
            if provider == "cohere":
                messages_for_llm = []
                for msg in chat_history:
                    if msg["role"] == "user":
                        messages_for_llm.append({"role": "USER", "message": msg["content"]})
                    elif msg["role"] == "assistant":
                        messages_for_llm.append({"role": "CHATBOT", "message": msg["content"]})
                    else:
                        messages_for_llm.append({"role": "SYSTEM", "message": msg["content"]})
            else:
                # OpenAI / others
                messages_for_llm = [{"role": m["role"], "content": m["content"]} for m in chat_history]

            # 7. Call LLM with full history
            response_text = await llm_client.chat(
                messages=messages_for_llm,
                system=system_text,
                documents=None
            )

            # 8. Append assistant message
            chat_history.append({"role": "assistant", "content": response_text})

            # 9. Save updated history
            await self.mongo_repository.save_chat_history(user_id, provider, chat_history)

            return {"answer": response_text}

        except Exception as e:
            logger.exception("Failed to answer question")
            return {"error": f"Failed to answer question: {str(e)}"}
