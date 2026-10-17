import os

import redis.asyncio as aioredis
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

redis_client=aioredis.Redis(host=os.getenv("REDIS_HOST"),
               port=int(os.getenv("REDIS_PORT")),
               db=int(os.getenv("REDIS_DB")),
               password=os.getenv("REDIS_PASSWORD"),
               decode_responses=True
               )

