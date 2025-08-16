import logging
from typing import List
from langchain.text_splitter import CharacterTextSplitter
from app.clients.cohere_embedding_client import CohereEmbeddingClient
from app.repositories.qdrant_repository import QdrantRepository
from qdrant_client.models import PointStruct, Filter, FieldCondition, MatchValue
import uuid

from app.exceptions.search_exceptions import (
    EmbeddingFailedException,
    VectorStorageException,
    SearchFailedException,
    VectorInsertionException
)

logger = logging.getLogger(__name__)

class SemanticSearchService:
    def __init__(self, cohere_client: CohereEmbeddingClient, qdrant_repository: QdrantRepository):
        self.cohere_client = cohere_client
        self.qdrant_repository = qdrant_repository
        self.splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=500,
            chunk_overlap=50
        )

    def split_text(self, text: str) -> List[str]:
        logger.info("Splitting text into chunks...")
        return self.splitter.split_text(text)

    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        try:
            logger.info(f"Embedding {len(texts)} chunks with Cohere")
            return self.cohere_client.embed(texts)
        except Exception as e:
            logger.error(f"Embedding failed: {e}")
            raise EmbeddingFailedException()

    def delete_user_vectors(self, username: str, filename: str = None):
        must_conditions = [FieldCondition(key="username", match=MatchValue(value=username))]
        if filename:
            must_conditions.append(FieldCondition(key="filename", match=MatchValue(value=filename)))
        q_filter = Filter(must=must_conditions)
        self.qdrant_repository.delete_collection(filter=q_filter)

    async def store_vectors(self, embeddings: List[List[float]], chunks: List[str], metadata: dict, file_id: str):
        try:
            payloads = [
                {"text": chunk, **metadata, "chunk_index": i}
                for i, chunk in enumerate(chunks)
            ]
            logger.info(f"Inserting {len(embeddings)} vectors into Qdrant")
            self.qdrant_repository.insert_vectors(embeddings, payloads, file_id)
        except Exception as e:
            logger.error(f"Failed to store vectors: {e}")
            raise VectorStorageException()

    async def search(self, query: str, username: str, file_id: str):
        try:
            query_embedding = self.cohere_client.embed([query])[0]
            logger.debug(f"Query embedding length: {len(query_embedding)}")
            results = self.qdrant_repository.search_vectors(
                query_vector=query_embedding,
                file_id=file_id,
                top_k=5
            )
            logger.debug(f"Qdrant search results: {results}")
            return results
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise SearchFailedException()

    def insert_vectors(self, embeddings: List[List[float]], payloads: List[dict]):
        logger.info("Inserting %d vectors into Qdrant...", len(embeddings))
        try:
            points = [
                PointStruct(
                    id=str(uuid.uuid4()),
                    vector=embedding,
                    payload=payload
                )
                for embedding, payload in zip(embeddings, payloads)
            ]
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            logger.info("Successfully inserted vectors into Qdrant.")
        except Exception as e:
            logger.error(f"Failed to insert vectors into Qdrant: {e}")
            raise VectorInsertionException()
