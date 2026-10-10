from core.mail import create_mail_insatance
from fastapi_mail import FastMail
from sqlalchemy.ext.asyncio import AsyncSession
from models import AsyncSessionFactory

async def get_session()->AsyncSession:
    session = AsyncSessionFactory()
    try:
        yield session
    finally:
        await session.close()

async def get_mail()->FastMail:
    return create_mail_insatance()