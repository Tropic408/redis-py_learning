from pydantic import BaseModel,Field
from typing import Annotated,Literal,List
from .agent import BodyInfoSchema

class PlanIn(BaseModel):
    gender: Annotated[Literal["男","女"],Field(...,description="性别")]
    height: Annotated[float,Field(...,gt=0,description="身高cm")]
    weight: Annotated[float,Field(...,gt=0,description="体重kg")]
    age: Annotated[int,Field(...,gt=0,description="年龄")]
    demand: Annotated[str,Field("",description="特殊需求")]

class PlanOut(BaseModel):
    plans: List[BodyInfoSchema]