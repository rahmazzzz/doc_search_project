import uuid
from cohere import Client
from app.core.config import settings

cohere_client = Client(settings.COHERE_API_KEY)

def embed_chunks(chunks: list):
    """
    Take a list of chunks (each with text),
    embed them with Cohere,
    and return the embeddings in the Qdrant-friendly format.
    """
    texts = [chunk["text"] for chunk in chunks]
    embeddings = cohere_client.embed(texts=texts).embeddings

    vectors = []
    for chunk, embedding in zip(chunks, embeddings):
        vectors.append({
            "id": str(uuid.uuid4()),  # unique ID for Qdrant
            "vector": embedding,      # the numeric vector
            "payload": {"text": chunk["text"]}  # extra metadata
        })

    return vectors


def embed_query(query: str):
    """
    Embed a search query.
    """
    return cohere_client.embed(texts=[query]).embeddings[0]
