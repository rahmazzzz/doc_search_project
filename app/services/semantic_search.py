import logging
from typing import List, Optional
from langchain.text_splitter import CharacterTextSplitter
from app.clients.cohere_client import CohereEmbeddingClient
from app.services.qdrant_service import QdrantService

logger = logging.getLogger(__name__)

class SemanticSearchService:
    def __init__(
        self,
        cohere_client: CohereEmbeddingClient,
        qdrant_service: QdrantService
    ):
        self.cohere_client = cohere_client
        self.qdrant_service = qdrant_service
        self.splitter = CharacterTextSplitter(separator="\n", chunk_size=500, chunk_overlap=50)

    def split_text(self, text: str) -> List[str]:
        logger.info("Splitting text into chunks...")
        return self.splitter.split_text(text)

    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        try:
            logger.info(f"Embedding {len(texts)} chunks with Cohere")
            # Note: Cohere client is synchronous, so run in thread or keep sync
            # If synchronous, remove await and just call directly
            embeddings = self.cohere_client.embed(texts)
            return embeddings
        except Exception as e:
            logger.error(f"Embedding failed: {e}")
            raise

    async def store_vectors(self, embeddings: List[List[float]], chunks: List[str], metadata: dict):
        try:
            payloads = []
            for i, chunk in enumerate(chunks):
                payload = {
                    "text": chunk,
                    **metadata,
                    "chunk_index": i,
                }
                payloads.append(payload)

            logger.info(f"Inserting {len(embeddings)} vectors into Qdrant")
            # QdrantService insert_vectors is synchronous, so call directly
            self.qdrant_service.insert_vectors(embeddings, payloads)
        except Exception as e:
            logger.error(f"Failed to store vectors: {e}")
            raise

    async def search(self, query: str, username: str):
        try:
            query_embedding = self.cohere_client.embed([query])
            print(f"Query embedding shape: {len(query_embedding[0])}")
            
            results = self.qdrant_service.search(
                query_vector=query_embedding[0],
                top_k=5,
                username=username
            )
            print(f"Qdrant search results: {results}")
            return results
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise