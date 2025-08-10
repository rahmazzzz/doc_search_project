from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.security.deps import get_current_user
from app.container.core_container import container
from app.models.user import User

router = APIRouter()

class QuestionRequest(BaseModel):
    question: str

@router.post("/ask")
async def ask_question(request: QuestionRequest, current_user: dict = Depends(get_current_user)):
    result = await container.llm_search_service.answer_question(
        user_id=current_user["username"],
        question=request.question
    )

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return result