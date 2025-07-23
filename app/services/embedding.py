import os
from cohere import Client
from app.core.config import settings

cohere_client = Client(settings.COHERE_API_KEY)

def embed_chunks(chunks: list):
    texts = [chunk["text"] for chunk in chunks]
    embeddings = cohere_client.embed(texts=texts).embeddings
    return [{"text": chunk["text"], "embedding": emb} for chunk, emb in zip(chunks, embeddings)]

def embed_query(query: str):
    return cohere_client.embed(texts=[query]).embeddings[0]
