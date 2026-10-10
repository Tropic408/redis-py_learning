import os
from pathlib import Path

from sqlalchemy.ext.asyncio import create_async_engine,AsyncSession
from sqlalchemy.orm import sessionmaker,DeclarativeBase
from sqlalchemy import MetaData
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

DB_URI = os.getenv("DB_URI")
if not DB_URI:
    raise RuntimeError("DB_URI 未设置，请检查 .env 或系统环境变量")

engine = create_async_engine(
    DB_URI,
    echo = True,
    pool_size = 10,
    max_overflow = 20,
    #获得连接超时时间（默认30s）
    pool_timeout = 10,
    #连接回收时间（默认-1永不回收）
    pool_recycle = 3600,
    #连接前是否预检查
    pool_pre_ping = True,
)

AsyncSessionFactory = sessionmaker(
    bind = engine,
    class_=AsyncSession,
    autoflush=True,
    expire_on_commit=False
)

class Base(DeclarativeBase):
    metadata = MetaData(naming_convention={
        #ix:index索引
        "ix":"ix_%(column_0_label)s",
        #uq:unique唯一约束
        "uq":"uq_%(table_name)s_%(column_0_name)s",
        #ck:check检查约束
        "ck":"ck_%(table_name)s_%(constraint_name)s",
        #fk:foreign key外键约束
        "fk":"fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        #pk:primary key主键约束
        "pk":"pk_%(table_name)s"
    })

from . import user
