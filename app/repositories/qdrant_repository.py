from typing import List, Optional
from app.clients.qdrant_client import QdrantDBClient
from qdrant_client.models import (
    PointStruct,
    VectorParams,
    Distance,
    Filter,
    FieldCondition,
    MatchValue
)
import logging

logger = logging.getLogger(__name__)

class QdrantRepository:
    def __init__(self, qdrant_client: QdrantDBClient):
        self.qdrant_client = qdrant_client
        self.collection_name = qdrant_client.collection_name
        self.client = qdrant_client.get_client()
        self._ensure_collection_exists()

    def _ensure_collection_exists(self):
        collections = self.client.get_collections().collections
        collection_names = [c.name for c in collections]
        if self.collection_name not in collection_names:
            logger.info(f"Creating Qdrant collection '{self.collection_name}' with vector size 1024")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=1024,
                    distance=Distance.COSINE
                )
            )

    def insert_vectors(self, points: List[PointStruct]):
        logger.info("Inserting %d vectors into Qdrant...", len(points))
        try:
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            logger.info("Successfully inserted vectors into Qdrant.")
        except Exception as e:
            logger.error(f"Failed to insert vectors into Qdrant: {e}")
            raise

    def delete_collection(self):
        try:
            self.client.delete_collection(collection_name=self.collection_name)
            logger.info(f"Deleted Qdrant collection '{self.collection_name}'")
        except Exception as e:
            logger.error(f"Error deleting Qdrant collection: {e}")
            raise

    def search_vectors(self, query_vector: List[float], top_k: int = 5, username: Optional[str] = None):
        try:
            logger.info(f"Searching top {top_k} vectors from Qdrant...")

            q_filter = None
            if username:
                q_filter = Filter(
                    must=[
                        FieldCondition(
                            key="username",
                            match=MatchValue(value=username)
                        )
                    ]
                )

            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=top_k,
                query_filter=q_filter
            )
            return results

        except Exception as e:
            logger.error(f"Error searching vectors in Qdrant: {e}")
            raise