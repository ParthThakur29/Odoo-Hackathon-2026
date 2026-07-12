import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from .database import get_db
from . import models

JWT_SECRET = os.getenv("JWT_SECRET", "your_secret_here")
JWT_ALGORITHM = "HS256"
JWT_EXPIRES_DAYS = 7


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except ValueError:
        return False


def create_access_token(employee_id: int, role: str) -> str:
    payload = {
        "id": employee_id,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(days=JWT_EXPIRES_DAYS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])


async def authenticate(request: Request, db: Session = Depends(get_db)) -> models.Employee:
    """Equivalent to the Express `authenticate` middleware."""
    token = request.cookies.get("token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    try:
        decoded = decode_token(token)
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    request.state.user_id = decoded.get("id")
    request.state.user_role = decoded.get("role")
    return decoded


def authorize(*roles: str):
    """Equivalent to the Express `authorize(...roles)` middleware factory."""

    async def _authorize(request: Request, user=Depends(authenticate)):
        user_role = request.state.user_role
        if not user_role:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        if roles and user_role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return user

    return _authorize


def get_user_id(request: Request) -> int:
    return request.state.user_id
