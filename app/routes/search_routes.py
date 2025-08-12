from fastapi import APIRouter, Depends, HTTPException, Query
from bson import ObjectId
from app.security.deps import get_current_user
from app.container.core_container import container

router = APIRouter()

@router.get("/ask")
async def semantic_search_route(
    query: str = Query(..., description="Search query text"),
    file_id: str = Query(None, description="Optional MongoDB file ID to filter results"),
    current_user: dict = Depends(get_current_user)
):
    # Validate file_id if provided
    if file_id:
        try:
            ObjectId(file_id)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid file ID format")

    try:
        results = await container.semantic_search_service.search(
            query=query,
            username=current_user["username"],
            file_id=file_id
        )
        return {"matches": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Semantic search failed: {str(e)}")
