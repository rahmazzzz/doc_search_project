from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, field_validator
from typing import Optional, List, Dict
import logging

from app.container.core_container import container
from app.clients.mistral_chat_client import MistralChatResponse
from app.security.deps import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)

# --- Request Model ---
class QuestionRequest(BaseModel):
    question: str
    file_id: str
    prompt_name: str
    provider_name: Optional[str] = "cohere"

    @field_validator("provider_name")
    def validate_provider(cls, v):
        allowed_providers = {"cohere", "openai", "mistral"}
        if v and v.lower() not in allowed_providers:
            raise ValueError(f"provider_name must be one of {allowed_providers}")
        return v.lower() if v else "cohere"


@router.post("/chat", response_model=MistralChatResponse)
async def ask_question(
    request: QuestionRequest,
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["sub"]
    provider = request.provider_name

    # fetch history
    history: List[Dict[str, str]] = await container.mongo_repository.get_chat_history(
        user_id, provider
    )
    history.append({"role": "user", "content": request.question})

    try:
        # 🔎 semantic search context (not directly returned, but used in service)
        await container.semantic_search_service.search(
            query=request.question,
            username=user_id,
            file_id=request.file_id
        )

        # 💡 call LLM service
        reply = await container.llm_search_service.answer_question(
            question=request.question,
            user_id=user_id,
            file_id=request.file_id,
            prompt_name=request.prompt_name,
            provider_name=provider,
            chat_history=history
        )

    except Exception as e:
        logger.exception("LLM service failed")
        raise HTTPException(status_code=500, detail=f"LLM service failed: {e}")

    if not reply or not getattr(reply, "answer", None):
        raise HTTPException(status_code=400, detail="No answer returned from LLM")

    # add assistant reply to history
    history.append({"role": "assistant", "content": reply.answer})
    await container.mongo_repository.save_chat_history(user_id, provider, history)

    #  ensure return is always a MistralChatResponse
    if isinstance(reply, MistralChatResponse):
        return reply
    else:
        return MistralChatResponse(answer=reply.answer, sources=[r.dict() for r in reply.sources])
