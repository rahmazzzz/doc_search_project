from app.clients.mongo_client import MongoDBClient
from app.clients.qdrant_client import QdrantDBClient
from app.clients.cohere_client import CohereEmbeddingClient
from app.services.mongo_service import MongoService
from app.services.qdrant_service import QdrantService
from app.services.processing import ProcessingService
from app.core.config import settings

# Initialize clients
mongo_client = MongoDBClient(
    uri=settings.MONGO_URI,
    db_name=settings.MONGODB_DATABASE
)

qdrant_client = QdrantDBClient(
    url=settings.QDRANT_URL,
    api_key=settings.QDRANT_API_KEY,
    collection_name=settings.QDRANT_COLLECTION
)

cohere_client = CohereEmbeddingClient(
    api_key=settings.COHERE_API_KEY
)

# Initialize services
mongo_service = MongoService(mongo_client)
qdrant_service = QdrantService(qdrant_client)
processing_service = ProcessingService(cohere_client)

# Dependency container
class Container:
    def __init__(self):
        self.mongo_service = mongo_service
        self.qdrant_service = qdrant_service
        self.processing_service = processing_service

# Exported container
container = Container()