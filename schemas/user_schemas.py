from pydantic import BaseModel,ConfigDict,Field,EmailStr,model_validator
from typing import Annotated,Literal,List


UsernameStr = Annotated[str,Field(...,min_length=4,max_length=20,description="用户名，长度为4-20个字符")]
RawPasswordStr = Annotated[str,Field(...,min_length=6,max_length=20,description="密码，长度为6-20个字符")]

class RegisterIn(BaseModel):
    email: EmailStr
    username: UsernameStr
    password: RawPasswordStr
    confirm_password:RawPasswordStr
    code: Annotated[str,Field(...,min_length=4,max_length=4,description="验证码，长度为4字符")]

    @model_validator(mode="after")
    def password_is_match(self)->"RegisterIn":
        password = self.password
        confirm_password = self.confirm_password
        if password != confirm_password:
            raise ValueError("密码不一致")
        return self

class UserCreateSchema(BaseModel):
    email: EmailStr
    password: RawPasswordStr
    username: UsernameStr

class LoginIn(BaseModel):
    email:EmailStr
    password: RawPasswordStr

class UserSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Annotated[int,Field(...)]
    email: EmailStr
    username: UsernameStr

class LoginOut(BaseModel):
    user: UserSchema
    access_token: str
    token_type: str = "bearer"
