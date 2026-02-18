from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Optional, TypedDict, Literal

from jose import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import JWT_SECRET_KEY, JWT_ALGORITHM

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
) -> int:
    """
    Strict auth dependency.
    - Missing token -> 403/401 from HTTPBearer
    - Invalid/expired -> 401 from decode_token()
    Returns: user_id as int (backwards compatible with your current routers).
    """
    token = credentials.credentials
    payload = decode_token(token)

    subject = payload.get("sub")
    if subject is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    try:
        return int(subject)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
