from datetime import datetime, timedelta, timezone
from jose import jwt
import time

from app.core.config import (
    JWT_SECRET_KEY,
    JWT_ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)

def create_access_token(
    subject: str,
    expires_delta: timedelta,
    extra: dict = None,
) -> tuple[str, datetime]:
    expires_at = datetime.now(tz=timezone.utc) + expires_delta

    payload = {
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
