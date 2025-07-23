from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
from app.core.config import settings

client = QdrantClient(url=settings.QDRANT_URL)

COLLECTION_NAME = "documents"

client.recreate_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=VectorParams(size=4096, distance=Distance.COSINE),
)

def upsert_embeddings(embeddings: list):
    points = []
    for i, item in enumerate(embeddings):
        points.append(PointStruct(id=i, vector=item["embedding"], payload={"text": item["text"]}))
    client.upsert(collection_name=COLLECTION_NAME, points=points)

def semantic_search(embedding):
    hits = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=embedding,
        limit=5
    )
    return [{"text": hit.payload["text"], "score": hit.score} for hit in hits]
