from fastapi import APIRouter, Query, Depends, HTTPException
from app.clients.qdrant_client import get_similar_chunks
from app.services.llm import call_llm
from app.auth.deps import get_current_user

router = APIRouter(prefix="/search", tags=["Search"])

@router.get("/", summary="Search your indexed documents")
async def search(
    query: str = Query(..., description="Your question to search for"),
    user=Depends(get_current_user)
):
    try:
        chunks = get_similar_chunks(query)
        if not chunks:
            raise HTTPException(status_code=404, detail="No matching chunks found")

        context = "\n\n".join([chunk["text"] for chunk in chunks])
        answer = call_llm(query, context)

        return {
            "query": query,
            "chunks_used": [chunk["text"] for chunk in chunks],
            "answer": answer,
            "user": user["username"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
