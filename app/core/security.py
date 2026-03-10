from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Optional, TypedDict, Literal

from jose import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session, joinedload

from app.core.config import JWT_SECRET_KEY, JWT_ALGORITHM
from app.db import get_db

security = HTTPBearer()


class TokenClaims(TypedDict, total=False):
    sub: str
    exp: int
    actor_type: Literal["user", "provider"]
    token_type: Literal["access", "refresh"]


def create_access_token(
    subject: str,
    expires_delta: timedelta,
    extra: Optional[dict[str, Any]] = None,
) -> tuple[str, datetime]:
    expires_at = datetime.now(tz=timezone.utc) + expires_delta

    payload: dict[str, Any] = {
        "sub": subject,
        "exp": int(expires_at.timestamp()),
    }

    if extra:
        payload.update(extra)

    token = jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )

    return token, expires_at


def decode_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )


def verify_token(token: str) -> int:
    payload = decode_token(token)
    subject = payload.get("sub")

    if subject is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    try:
        return int(subject)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """
    Strict auth dependency.
    - Missing token -> 403/401 from HTTPBearer
    - Invalid/expired -> 401 from decode_token()
    - Token not in DB (revoked/logged out) -> 401
    Returns: full User ORM object with role eagerly loaded.
    """
    from app.models.user import User
    from app.models.personal_access_token import PersonalAccessToken

    token = credentials.credentials
    payload = decode_token(token)

    subject = payload.get("sub")
    if subject is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    try:
        user_id = int(subject)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    db_token = (
        db.query(PersonalAccessToken)
        .filter(
            PersonalAccessToken.access_token == token,
            PersonalAccessToken.user_id == user_id,
        )
        .first()
    )

    if db_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
        )

    user = (
        db.query(User)
        .options(joinedload(User.role))
        .filter(User.id == user_id)
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user
