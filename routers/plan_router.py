import hashlib
import json

from fastapi import APIRouter,Depends

from core.agent import generate_plan
from core.redis_client import redis_client
from schemas.body_info import PlanIn,PlanOut
from core.auth import get_current_user_id

router = APIRouter(prefix="/plan")

@router.post("",response_model=PlanOut)
async def take_plan(
        data: PlanIn,
        user_id: int = Depends(get_current_user_id),
):
    #1.拼key
    key = f"plan:{data.gender}:{data.height}:{data.weight}:{data.age}:" \
          f"{hashlib.md5(data.demand.encode()).hexdigest()}"
    #2.查缓存
    cached = await redis_client.get(key)
    if cached is not None:
        return PlanOut(plans=json.loads(cached))
    #3.未命中，调模型
    plan_result = await generate_plan(data)
    #4.存缓存，value是plan-json
    await redis_client.setex(key,86400,
                             json.dumps([p.model_dump() for p in plan_result.plans]))
    return PlanOut(plans=plan_result.plans)
