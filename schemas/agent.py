from pydantic import BaseModel, Field, field_validator
from typing import Annotated,List

class BodyInfoSchema(BaseModel):
    bmi: Annotated[str,Field(...,description="体重指数")]
    plan: Annotated[str,Field(...,description="计划表")]
    goal: Annotated[str,Field(...,description="目标")]
    reason: Annotated[str,Field(...,description="计划理由")]
    food_suggestion: Annotated[str,Field(...,description="饮食建议")]
    rest: Annotated[str,Field(...,description="休息建议")]

    @field_validator('*', mode='before')
    @classmethod
    def _list_to_str(cls, v):
        if isinstance(v, list):
            return '\n'.join(str(x) for x in v)
        return v

class BodyInfoResultSchema(BaseModel):
    plans: List[BodyInfoSchema]