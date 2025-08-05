from fastapi import APIRouter, Depends
from app.deps import get_current_user
from app.container.core_container import container

router = APIRouter()

@router.get("/")
async def search(q: str, user: dict = Depends(get_current_user)):
    embedding = container.processing_service.embed_texts([q])[0]
    results = container.qdrant_service.search_vectors(embedding)
    return [{"score": hit.score, "text": hit.payload["text"]} for hit in results]
