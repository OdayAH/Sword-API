# app/services/token_service.py
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS
from app.core.jwt import create_access_token as create_jwt
from app.models.personal_access_token import PersonalAccessToken
from app.models.user import User

def issue_and_store_tokens(db: Session, user: User) -> PersonalAccessToken:
    access_token, access_exp = create_jwt(
        subject=str(user.id),
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        extra={"type": "access"},
    )

    refresh_token, refresh_exp = create_jwt(
        subject=str(user.id),
        expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        extra={"type": "refresh"},
    )

    now = datetime.now(timezone.utc)

    row = PersonalAccessToken(
        user_id=user.id,
        access_token=access_token,
        refresh_token=refresh_token,
        issued_at=now,
        access_expires_at=access_exp,
        refresh_expires_at=refresh_exp,
    )

    db.add(row)
    db.commit()
    db.refresh(row)
    return row
