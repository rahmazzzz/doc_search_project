from qdrant_client import QdrantClient, models
from app.core.config import settings
from app.services.embedding import embed_query  # Make sure this exists!

client = QdrantClient(url=settings.QDRANT_URL)

def ensure_collection_exists(vector_size: int):
    if not client.collection_exists(collection_name=settings.QDRANT_COLLECTION):
        client.create_collection(
            collection_name=settings.QDRANT_COLLECTION,
            vectors_config=models.VectorParams(
                size=vector_size,
                distance=models.Distance.COSINE
            )
        )
        print(f"✅ Created collection `{settings.QDRANT_COLLECTION}` with vector size {vector_size}")

def upsert_embeddings(vectors):
    """
    Ensure the collection exists, then upsert embeddings.
    """
    if not vectors:
        raise ValueError("No vectors to upsert!")

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
    print(f"✅ Upserted {len(vectors)} vectors to `{settings.QDRANT_COLLECTION}`")

def get_similar_chunks(query: str, limit=5):
    """
    Embed the query and search for similar vectors.
    """
    query_vector = embed_query(query)
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
    return chunks
