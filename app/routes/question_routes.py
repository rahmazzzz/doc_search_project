from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, field_validator
from typing import Optional

from app.security.deps import get_current_user
from app.container.core_container import container
from app.models.user import User

router = APIRouter()

class QuestionRequest(BaseModel):
    question: str
    file_id: str
    prompt_name: str
    provider_name: Optional[str] = "cohere"  # default to cohere

    @field_validator("provider_name")
    def validate_provider(cls, v):
        allowed_providers = {"cohere", "openai"}  # keep consistent with factory
        if v and v.lower() not in allowed_providers:
            raise ValueError(f"provider_name must be one of {allowed_providers}")
        return v.lower() if v else "cohere"


@router.post("/ask")
async def ask_question(
    request: QuestionRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Route delegates orchestration to LLMSearchService.
    LLMSearchService will pick the LLM client via LLMChatFactory based on provider_name.
    """
    # Use container's llm_search_service and pass provider_name to the service method
    result = await container.llm_search_service.answer_question(
        user_id=current_user["sub"],
        provider_name=request.provider_name,
        question=request.question,
        prompt_name=request.prompt_name,
        file_id=request.file_id
    )

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return result
