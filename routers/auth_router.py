from fastapi import APIRouter,Query,Depends,HTTPException
from pydantic import EmailStr
from typing import Annotated

from core.auth import create_access_token
from dependencies import get_mail,get_session
from fastapi_mail import FastMail,MessageSchema,MessageType
from models import AsyncSession
import string
import random
from aiosmtplib import SMTPResponseException

from models.user import User
from repository.user_repo import EmailCodeRepository,UserRepository
from schemas import ResponseOut
from schemas.user_schemas import RegisterIn, UserCreateSchema, LoginIn, LoginOut

router = APIRouter(prefix="/auth",tags=["user"])

@router.get("/code",response_model=ResponseOut)
async def get_email_code(
        email:Annotated[EmailStr,Query(...)],
        mail:FastMail = Depends(get_mail),
        session:AsyncSession=Depends(get_session),
):
    #1生成四位数验证码
    source = string.digits * 4
    code = ''.join(random.sample(source,4))
    #2创建消息对象
    message = MessageSchema(
        subject="【Fitness_Assistant】验证码",
        recipients=[email],
        body=f"您的验证码是{code}，请在10分钟内使用",
        subtype=MessageType.plain
    )
    try:
        await mail.send_message(message)
    except SMTPResponseException as e:
        if e.code == -1 and b"\\x00\\x00\\x00\\x00" in str(e).encode():
            print("忽略QQ邮箱SMTP关闭阶段的非标准响应（邮件已成功发送）")
        else:
            raise HTTPException(500,detail="邮件发送失败，请重试！")
    # 3将验证码存入数据库
    email_code_repo = EmailCodeRepository(session=session)
    await email_code_repo.create(str(email), code)
    return ResponseOut()

@router.post("/register",response_model=ResponseOut)
async def register(data:RegisterIn,session:AsyncSession = Depends(get_session)):
    user_repo = UserRepository(session)
    #1.判断邮箱是否存在
    email_exist = await user_repo.email_is_exist(email=str(data.email))
    if email_exist:
        raise HTTPException(400,detail="邮箱已存在")
    #2.判断验证码是否正确
    email_code_repo = EmailCodeRepository(session=session)
    email_code_match = await email_code_repo.check_email_code(email=str(data.email),code=str(data.code))
    if not email_code_match:
        raise HTTPException(400,detail="邮箱或验证码错误")
    try:
        await user_repo.create(UserCreateSchema(email=str(data.email),password=data.password,username=data.username))
    except Exception as e:
        raise HTTPException(500,detail=str(e))
    return ResponseOut()


@router.post("/login",response_model=LoginOut)
async def login(
        data: LoginIn,
        session: AsyncSession = Depends(get_session),
):
    #1.创建user_repo对象
    user_repo = UserRepository(session=session)
    #2.根据邮箱查找用户
    user: User|None = await user_repo.get_by_email(str(data.email))
    if not user:
        raise HTTPException(400,detail="该用户不存在")
    if not user.check_password(data.password):
        raise HTTPException(400,detail="邮箱或密码错误")
    #3.生成JWToken
    token = create_access_token(user.id)
    return LoginOut(user=user, access_token=token)
