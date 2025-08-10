import logging
from app.clients.cohere_client import CohereEmbeddingClient
from app.repositories.qdrant_repository import QdrantRepository
from app.repositories.mongo_repository import MongoRepository
from app.services.semantic_search import SemanticSearchService
from app.prompts.english_prompt import generate_english_prompt
from app.prompts.arabic_prompt import generate_arabic_prompt

logger = logging.getLogger(__name__)

class LLMSearchService:
    def __init__(
        self,
        semantic_search_service: SemanticSearchService,
        cohere_client: CohereEmbeddingClient,
        qdrant_repository: QdrantRepository,
        mongo_repository: MongoRepository,
    ):
        self.semantic_search_service = semantic_search_service
        self.cohere_client = cohere_client
        self.qdrant_repository = qdrant_repository
        self.mongo_repository = mongo_repository

    async def answer_question(self, user_id: str, question: str, language: str = "english") -> dict:
        try:
            # Embed the question
            embedding = self.cohere_client.embed([question])[0]

            # Search Qdrant for relevant context by user_id
            results = self.qdrant_repository.search_vectors(embedding, username=user_id)
            if not results:
                return {"error": "No relevant context found."}

            # Extract top 3 text chunks as context
            context = "\n".join(hit.payload["text"] for hit in results[:3])

            # Generate prompt based on language
            if language.lower() == "arabic":
                prompt = generate_arabic_prompt(question, context)
            else:
                prompt = generate_english_prompt(question, context)

            # Send prompt to Cohere chat and get response
            response = self.cohere_client.chat(
                message=prompt,
                documents=[]
            )

            return {"answer": response}

        except Exception as e:
            logger.error(f"Failed to answer question: {e}")
            return {"error": f"Failed to answer question: {str(e)}"}
