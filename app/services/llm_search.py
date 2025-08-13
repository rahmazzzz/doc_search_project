import logging
from typing import Optional, Dict, Any

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
    ) -> Dict[str, Any]:
        """
        Answer a question using the specified LLM provider.

        :param user_id: ID of the current user
        :param question: User's question
        :param file_id: Optional file ID for context restriction
        :param prompt_name: Name of the prompt template
        :param language: Language of the response
        :param provider_name: Which LLM to use ("cohere" or "openai")
        """
        try:
            provider = (provider_name or settings.LLM_PROVIDER).lower()

            # 1. Instantiate LLM client for this request
            llm_client = LLMChatFactory.get_client(provider)

            # 2. Fetch prompt template
            prompt_doc = await self.prompt_repository.get_prompt_by_name(prompt_name)
            if not prompt_doc:
                return {"error": f"No prompt found with name '{prompt_name}'"}

            system_text = prompt_doc.get("system", "")
            user_template = prompt_doc.get("user", "")

            # 3. Embed the question
            embedding = self.cohere_embedding_client.embed([question])
            query_vector = embedding[0]

            # 4. Search for relevant chunks
            results = self.qdrant_repository.search_vectors(
                query_vector=query_vector,
                file_id=file_id,
                top_k=5
            )
            if not results:
                return {"error": "No relevant context found."}

            # 5. Extract top chunks
            context_chunks = [
                str(hit.payload.get("text", "")) for hit in results[:3]
            ]
            context = "\n".join(context_chunks)

            # 6. Build the user prompt
            final_user_prompt = user_template.format(
                question=question,
                context=context,
                language=language
            )

            # 7. Call the LLM
            response_text =  llm_client.chat(
     message=final_user_prompt,
    system=system_text)

            return {"answer": response_text}

        except Exception as e:
            logger.exception("Failed to answer question")
            return {"error": f"Failed to answer question: {str(e)}"}
