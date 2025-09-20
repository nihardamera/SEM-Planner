from fastapi import APIRouter, HTTPException
from models import PlanRequest, PlanResponse
from sem_plan import generate_full_sem_plan

router = APIRouter()

@router.post("/plan", response_model=PlanResponse, summary="Generate a full SEM Plan")
async def create_sem_plan(request: PlanRequest):
    try:
        plan = await generate_full_sem_plan(request)
        return plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

