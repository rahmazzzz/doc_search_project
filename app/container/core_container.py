from app.clients.mongo_client import MongoDBClient
from app.clients.qdrant_client import QdrantDBClient
from app.clients.cohere_client import CohereEmbeddingClient

from app.repositories.mongo_repository import MongoRepository
from app.repositories.qdrant_repository import QdrantRepository

from app.services.mongo_service import MongoService
from app.services.qdrant_service import QdrantService
from app.services.embedding import EmbeddingService
from app.services.llm import LLMService

from app.core.config import settings

# Initialize database clients
mongo_client = MongoDBClient(
    uri=settings.MONGO_URI,
    db_name=settings.MONGODB_DATABASE
)

qdrant_client = QdrantDBClient(
    url=settings.QDRANT_URL,
    api_key=settings.QDRANT_API_KEY,
    collection_name=settings.QDRANT_COLLECTION
)

# Initialize embedding client
cohere_client = CohereEmbeddingClient(
    api_key=settings.COHERE_API_KEY
)

# Initialize repositories
mongo_repository = MongoRepository(mongo_client)
qdrant_repository = QdrantRepository(qdrant_client)

# Initialize services
mongo_service = MongoService(mongo_repository)
qdrant_service = QdrantService(qdrant_repository)
embedding_service = EmbeddingService(cohere_client=cohere_client)
llm_service = LLMService(
    qdrant_service=qdrant_service,
    cohere_client=cohere_client,
    embedding_service=embedding_service,
    mongo_service=mongo_service
)

# Dependency container
class Container:
    def __init__(self):
        self.mongo_client = mongo_client
        self.qdrant_client = qdrant_client
        self.cohere_client = cohere_client

        self.mongo_repository = mongo_repository
        self.qdrant_repository = qdrant_repository

        self.mongo_service = mongo_service
        self.qdrant_service = qdrant_service
        self.embedding_service = embedding_service
        self.llm_service = llm_service

# Exported container instance
container = Container()
