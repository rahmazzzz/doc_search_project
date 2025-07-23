from fastapi import APIRouter, Query
from app.core.config import settings
from app.services.qdrant_client import get_similar_chunks
from app.services.llm import call_llm

router = APIRouter()

@router.get("/")
async def search(query: str = Query(..., description="Your question to search for")):
    chunks = get_similar_chunks(query)
    context = "\n\n".join([chunk["text"] for chunk in chunks])
    answer = call_llm(query, context)
    return {
        "query": query,
        "chunks_used": [chunk["text"] for chunk in chunks],
        "answer": answer
    }
