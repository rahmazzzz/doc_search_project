from fastapi import APIRouter, Query
from app.services.embedding import embed_query
from app.services.mongo_client import text_search
from app.services.qdrant_client import semantic_search

router = APIRouter()

@router.get("/")
async def search(query: str, mode: str = "hybrid"):
    results = []
    if mode in ["fulltext", "hybrid"]:
        results.extend(text_search(query))
    if mode in ["semantic", "hybrid"]:
        embedding = embed_query(query)
        results.extend(semantic_search(embedding))
    return {"results": results}
