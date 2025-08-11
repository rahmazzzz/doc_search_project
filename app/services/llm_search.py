import logging
from app.clients.cohere_embedding_client import CohereEmbeddingClient
from app.repositories.qdrant_repository import QdrantRepository
from app.repositories.mongo_repository import MongoRepository
from app.repositories.prompt_repository import PromptRepository
from app.services.semantic_search import SemanticSearchService

logger = logging.getLogger(__name__)

class LLMSearchService:
    def __init__(
        self,
        semantic_search_service,
        cohere_embedding_client,
        cohere_chat_client,
        qdrant_repository,
        mongo_repository,
        prompt_repository
    ):
        self.semantic_search_service = semantic_search_service
        self.cohere_embedding_client = cohere_embedding_client
        self.cohere_chat_client = cohere_chat_client
        self.qdrant_repository = qdrant_repository
        self.mongo_repository = mongo_repository
        self.prompt_repository = prompt_repository

    async def answer_question(
        self,
        user_id: str,
        question: str,
        prompt_name: str = "default",
        language: str = "english",
        file_id: str = None
    ) -> dict:
        """
        Search relevant context from vector DB, build prompt from MongoDB template,
        and get an answer from the LLM.
        """
        try:
            # 1. Fetch prompt template from MongoDB
            prompt_doc = await self.prompt_repository.get_prompt_by_name(prompt_name)
            if not prompt_doc:
                return {"error": f"No prompt found with name '{prompt_name}'"}

            system_text = prompt_doc.get("system", "")
            user_template = prompt_doc.get("user", "")

            # 2. Embed the question
            embedding = self.cohere_embedding_client.embed([question])
            query_vector = embedding[0]

            # 3. Search Qdrant for relevant chunks
            results = self.qdrant_repository.search_vectors(
                query_vector=query_vector,
                file_id=file_id,
                top_k=5
            )
            if not results:
                return {"error": "No relevant context found."}

            # 4. Extract clean text chunks
            context_chunks = []
            for hit in results[:3]:
                text_chunk = hit.payload.get("text", "")
                context_chunks.append(str(text_chunk))
            context = "\n".join(context_chunks)

            # 5. Build the final prompt by replacing placeholders
            final_user_prompt = user_template.format(question=question, context=context)

            # 6. Call Cohere LLM
            response = self.cohere_chat_client.chat(message=final_user_prompt, system=system_text)

            return {"answer": response}

        except Exception as e:
            logger.exception("Failed to answer question")
            return {"error": f"Failed to answer question: {str(e)}"}

    