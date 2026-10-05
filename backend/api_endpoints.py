import logging

from fastapi import APIRouter, HTTPException

import keyword_planner
import llm_calls
from models import PlanRequest, PlanResponse
from sem_plan import generate_full_sem_plan

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", summary="Liveness check and configuration status")
def health() -> dict:
    return {
        "status": "ok",
        "language_model_configured": llm_calls.is_configured(),
        "keyword_planner_configured": keyword_planner.is_configured(),
    }


# A plain def (not async def): the work is blocking network I/O (page fetch,
# Groq, Google Ads), so FastAPI runs it in its threadpool.
@router.post(
    "/plan",
    response_model=PlanResponse,
    summary="Generate a Google Ads plan",
    responses={502: {"description": "A language model call failed"}},
)
def create_sem_plan(request: PlanRequest) -> PlanResponse:
    try:
        return generate_full_sem_plan(request)
    except llm_calls.LLMError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from None
    except Exception:
        logger.exception("Unexpected error while generating a plan")
        raise HTTPException(
            status_code=500,
            detail="Unexpected error while generating the plan. Details are in the backend log.",
        ) from None
