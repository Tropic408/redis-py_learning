import os
from pathlib import Path

from fastapi_mail import FastMail,ConnectionConfig
from pydantic import SecretStr,EmailStr
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")


def create_mail_insatance()->FastMail:
    """创建fastmail实例（每次调用后返回新实例，线程/协程安全）"""
    mail_config = ConnectionConfig(
        MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
        MAIL_PASSWORD=SecretStr(os.getenv("MAIL_PASSWORD")),
        MAIL_FROM=os.getenv("MAIL_FROM"),
        MAIL_PORT=int(os.getenv("MAIL_PORT", "587")),
        MAIL_SERVER=os.getenv("MAIL_SERVER"),
        MAIL_FROM_NAME=os.getenv("MAIL_FROM_NAME"),
        MAIL_STARTTLS=os.getenv("MAIL_STARTTLS", "True").lower() == "true",
        MAIL_SSL_TLS=os.getenv("MAIL_SSL_TLS", "False").lower() == "true",
        USE_CREDENTIALS=True,
        VALIDATE_CERTS=True,
    )
    return FastMail(mail_config)
