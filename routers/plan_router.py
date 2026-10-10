from fastapi import APIRouter,Depends

from core.agent import generate_plan
from schemas.body_info import PlanIn,PlanOut
from core.auth import get_current_user_id

router = APIRouter(prefix="/plan")

@router.post("",response_model=PlanOut)
async def take_plan(
        data: PlanIn,
        user_id: int = Depends(get_current_user_id),
):
    plan_result = await generate_plan(data)
    return PlanOut(plans=plan_result.plans)
