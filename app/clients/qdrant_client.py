import logging
from qdrant_client import QdrantClient, models
from qdrant_client.http.exceptions import UnexpectedResponse
from app.core.config import settings
from app.services.embedding import embed_query  # Assumes this returns a list[float]

# Set up logging
logger = logging.getLogger(__name__)

# Initialize Qdrant client
client = QdrantClient(url=settings.QDRANT_URL)


def ensure_collection_exists(vector_size: int):
    """
    Create the collection if it doesn't already exist.
    """
    try:
        if not client.collection_exists(collection_name=settings.QDRANT_COLLECTION):
            client.create_collection(
                collection_name=settings.QDRANT_COLLECTION,
                vectors_config=models.VectorParams(
                    size=vector_size,
                    distance=models.Distance.COSINE
                )
            )
            logger.info(f" Created collection `{settings.QDRANT_COLLECTION}` with vector size {vector_size}")
    except Exception as e:
        logger.exception(" Failed to ensure Qdrant collection exists")
        raise


def upsert_embeddings(vectors: list) -> bool:
    """
    Upserts embeddings into Qdrant collection.
    Returns True on success, False on failure.
    """
    if not vectors:
        logger.error(" No vectors to upsert.")
        return False

    try:
        vector_size = len(vectors[0]["vector"])
        ensure_collection_exists(vector_size)

        client.upsert(
            collection_name=settings.QDRANT_COLLECTION,
            points=[
                models.PointStruct(
                    id=vec["id"],
                    vector=vec["vector"],
                    payload=vec["payload"]
                )
                for vec in vectors
            ]
        )

        logger.info(f" Upserted {len(vectors)} vectors to `{settings.QDRANT_COLLECTION}`")
        return True
    except Exception as e:
        logger.exception(" Failed to upsert embeddings to Qdrant")
        return False


def get_similar_chunks(query: str, limit: int = 5) -> list:
    """
    Embeds the query and retrieves similar chunks from Qdrant.
    """
    try:
        query_vector = embed_query(query)
        if not query_vector:
            logger.error(" Failed to generate query embedding")
            return []

        search_result = client.search(
            collection_name=settings.QDRANT_COLLECTION,
            query_vector=query_vector,
            limit=limit
        )

        chunks = []
        for hit in search_result:
            payload = hit.payload or {}
            payload["score"] = hit.score
            chunks.append(payload)

        logger.info(f"🔍Found {len(chunks)} similar chunks for query")
        return chunks

    except Exception as e:
        logger.exception(" Failed to search Qdrant collection")
        return []
