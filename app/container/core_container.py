from app.clients.nosqldb_client import MongoDBClient
from app.clients.vectordb_client import QdrantDBClient
from app.clients.cohere_embedding_client import CohereEmbeddingClient

from app.repositories.mongo_repository import MongoRepository
from app.repositories.qdrant_repository import QdrantRepository
from app.repositories.prompt_repository import PromptRepository

from app.services.file_processing import FileProcessingService
from app.services.semantic_search import SemanticSearchService
from app.services.llm_search import LLMSearchService

from app.core.config import settings

# === Clients ===
mongo_client = MongoDBClient(
    uri=settings.MONGO_URI,
    db_name=settings.MONGODB_DATABASE
)

qdrant_client = QdrantDBClient(
    url=settings.QDRANT_URL,
    api_key=settings.QDRANT_API_KEY,
    collection_name=settings.QDRANT_COLLECTION,
)

cohere_embedding_client = CohereEmbeddingClient(api_key=settings.COHERE_API_KEY)

# === Repositories ===
mongo_repository = MongoRepository(mongo_client)
qdrant_repository = QdrantRepository(qdrant_client)
prompt_repository = PromptRepository(mongo_client.db)

# === Services ===
semantic_search_service = SemanticSearchService(
    cohere_client=cohere_embedding_client,
    qdrant_repository=qdrant_repository
)

file_processing_service = FileProcessingService(
    mongo_repository=mongo_repository,
    semantic_search_service=semantic_search_service
)

# LLMSearchService no longer needs provider at init
llm_search_service = LLMSearchService(
    semantic_search_service=semantic_search_service,
    cohere_embedding_client=cohere_embedding_client,
    qdrant_repository=qdrant_repository,
    mongo_repository=mongo_repository,
    prompt_repository=prompt_repository
)

# === Container Class ===
class Container:
    def __init__(self):
        self.mongo_client = mongo_client
        self.qdrant_client = qdrant_client
        self.cohere_client = cohere_embedding_client

        self.mongo_repository = mongo_repository
        self.qdrant_repository = qdrant_repository
        self.prompt_repository = prompt_repository

        self.semantic_search_service = semantic_search_service
        self.file_processing_service = file_processing_service
        self.llm_search_service = llm_search_service

        self.file_search_service = file_processing_service


container = Container()
