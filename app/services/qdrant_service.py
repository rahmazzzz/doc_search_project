from typing import List, Optional
from qdrant_client.models import PointStruct
from app.repositories.qdrant_repository import QdrantRepository
import uuid

class QdrantService:
    def __init__(self, qdrant_repository: QdrantRepository):
        self.qdrant_repository = qdrant_repository

    def insert_vectors(self, embeddings: List[List[float]], metadata: List[dict]):
        points = [
            PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload=meta
            )
            for embedding, meta in zip(embeddings, metadata)
        ]
        self.qdrant_repository.insert_vectors(points)

    def delete_collection(self):
        self.qdrant_repository.delete_collection()

    def search(self, query_vector: List[float], top_k: int = 5, username: Optional[str] = None):
        return self.qdrant_repository.search_vectors(
            query_vector=query_vector,
            top_k=top_k,
            username=username  # Pass username to repository (if filtering is supported)
        )
