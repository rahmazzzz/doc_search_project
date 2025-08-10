from fastapi import APIRouter, Depends, Query
from app.security.deps import get_current_user
from app.container.core_container import container

router = APIRouter()

@router.get("/")
async def search(q: str = Query(..., min_length=1), user: dict = Depends(get_current_user)):
   results = await container.semantic_search_service.search(query=q, username=user["username"])
   return results