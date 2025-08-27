# app/routes/orchestrator_routes.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List

from app.container.core_container import container
from app.security.deps import get_current_user

router = APIRouter(prefix="/orchestrator", tags=["Orchestrator"])

# ----- Pydantic models -----
class OrchestratorRequest(BaseModel):
    query: str
    context: Optional[str] = None  # e.g., file_id, task type, etc.

class OrchestratorResponse(BaseModel):
    agent: str                # which agent handled it (search, upload, LLM, etc.)
    result: str               # final response
    steps: Optional[List[str]] = None  # reasoning / orchestration steps


# ----- Route -----
@router.post("/", response_model=OrchestratorResponse)
async def orchestrate_task(
    payload: OrchestratorRequest,
    current_user: dict = Depends(get_current_user)  # JWT provides user info
):
    """
    Orchestrator agent routes user queries between:
    - document search
    - web search (Tavily)
    - LLM (Mistral) for decision & synthesis
    """
    orchestrator = container.orchestrator_service
    username = current_user.get("username")
    file_id = payload.context

    try:
        # Run orchestration pipeline
        decision = await orchestrator.answer(
            query=payload.query,
            username=username,
            file_id=file_id
        )

        # Safely extract decision keys
        final_answer = decision.get("final_answer") if isinstance(decision, dict) else str(decision)
        agent_decision = decision.get("decision") if isinstance(decision, dict) else "unknown"

        return OrchestratorResponse(
            agent="orchestrator_agent",
            result=final_answer or "",
            steps=[
                "Received query",
                "Searched documents",
                "Searched web (Tavily)",
                "Mistral decided best source",
                f"Decision: {agent_decision or 'unknown'}"
            ]
        )

    except Exception as e:
        # Never let API return 500 due to missing keys or LLM errors
        return OrchestratorResponse(
            agent="orchestrator_agent",
            result=str(e),
            steps=["Error occurred during orchestration"]
        )
