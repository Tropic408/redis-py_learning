from fastapi import FastAPI,Depends
from fastapi_mail import FastMail, MessageSchema, MessageType
from aiosmtplib import SMTPResponseException
from routers.auth_router import router as auth_router
from routers.plan_router import router as plan_router
from dependencies import get_mail

app = FastAPI()

app.include_router(auth_router)
app.include_router(plan_router)

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

@app.get("/mail/test")
async def mail_test(
        email: str,
        mail: FastMail = Depends(get_mail)
):
    message = MessageSchema(
        subject="hello",
        recipients=[email],
        body=f"hello{email}",
        subtype=MessageType.plain,
    )
    try:
        await mail.send_message(message)
    except SMTPResponseException as e:
        if e.code == -1 and b"\\x00\\x00\\x00\\x00" in str(e).encode():
            print("忽略QQ邮箱SMTP关闭阶段的非标准响应（邮件已成功发送）")
    return {"message": "邮件发送成功"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
