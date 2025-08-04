from fastapi import APIRouter, Query, Depends
from app.core.config import settings
from app.services.qdrant_client import get_similar_chunks
from app.services.llm import call_llm
from app.auth.deps import get_current_user

router = APIRouter()

@router.get("/")
async def search(
    query: str = Query(..., description="Your question to search for"),
    user=Depends(get_current_user)
):
    print(f" User '{user['username']}' is searching: {query}")

    chunks = get_similar_chunks(query)
    context = "\n\n".join([chunk["text"] for chunk in chunks])
    answer = call_llm(query, context)

    return {
        "query": query,
        "chunks_used": [chunk["text"] for chunk in chunks],
        "answer": answer,
        "user": user["username"]
    }
