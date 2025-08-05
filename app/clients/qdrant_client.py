from qdrant_client import QdrantClient
import logging

logger = logging.getLogger(__name__)

class QdrantDBClient:
    def __init__(self, url: str, collection_name: str, api_key: str = None):
        self.collection_name = collection_name
        try:
            self.client = QdrantClient(url=url, api_key=api_key)
            logger.info("Initialized Qdrant client for collection '%s'.", self.collection_name)
        except Exception as e:
            logger.error("Failed to initialize QdrantClient: %s", e)
            raise

    def get_client(self):
        return self.client
