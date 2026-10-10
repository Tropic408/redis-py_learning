from pydantic import BaseModel,Field
from typing import Annotated,Literal

class ResponseOut(BaseModel):
    """
    用于一些视图函数只需要返回操作结果的模型
    """
    result:Annotated[Literal["success","failure"],Field("success",description="操作结果")]