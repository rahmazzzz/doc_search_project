from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, field_validator
from typing import Optional, List, Dict

from app.security.deps import get_current_user
from app.container.core_container import container

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


@router.post("/chat")
async def ask_question(
    request: QuestionRequest,
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["sub"]
    provider = request.provider_name

    # Fetch previous history
    history: List[Dict[str, str]] = await container.mongo_repository.get_chat_history(
        user_id, provider
    )

    # Append new user message
    history.append({"role": "user", "content": request.question})

    # Call LLM with chat history
    try:
        reply = await container.llm_search_service.answer_question(
            user_id=user_id,
            provider_name=provider,
            question=request.question,
            prompt_name=request.prompt_name,
            file_id=request.file_id,
            chat_history=history  # renamed param
        )
    except TypeError:
        raise HTTPException(status_code=500, detail="LLM service signature mismatch")

    if not reply or "answer" not in reply:
        raise HTTPException(status_code=400, detail=reply.get("error", "Unknown error"))

    # Append assistant reply
    history.append({"role": "assistant", "content": reply["answer"]})

    # Save updated chat history
    await container.mongo_repository.save_chat_history(user_id, provider, history)

    # Return latest assistant reply
    return {"answer": reply["answer"]}
