"""JWT authentication helpers built on PyJWT."""

import os
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

JWT_SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY",
    "ai_name-change-this-secret-to-at-least-32-bytes",
)
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))

bearer_scheme = HTTPBearer(auto_error=False)


def create_access_token(user_id: int) -> str:
    """Create a signed JWT for the given user id."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "user_id": user_id,
        "iat": now,
        "exp": now + timedelta(minutes=JWT_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    """Decode and validate a JWT, returning its claims."""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="登录状态无效或已过期",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    if "user_id" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token缺少用户信息",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload


def get_current_user_id(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(bearer_scheme),
    ],
) -> int:
    """FastAPI dependency that reads the user id from Authorization headers."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="请先登录",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(credentials.credentials)
    return int(payload["user_id"])
