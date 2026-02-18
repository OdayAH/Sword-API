from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from app.db import get_db
from app.models.user import User
from app.models.roles import Role
from app.models.personal_access_token import PersonalAccessToken
from app.services.token_service import issue_and_store_tokens
from app.core.security import get_current_user
from app.core.cache import cache_manager
from app.core.rate_limit import limiter, LOGIN_LIMIT

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RoleResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


@router.get("/roles", response_model=list[RoleResponse])
def get_roles(db: Session = Depends(get_db)):
    roles = db.query(Role).order_by(Role.id).all()
    if not roles:
        raise HTTPException(status_code=500, detail="No roles found in database")
    return roles


@router.post("/login")
@limiter.limit(LOGIN_LIMIT)
def login(request: Request, payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()

    if not user or user.password != payload.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token_data = issue_and_store_tokens(db, user)
    if not token_data or not token_data.access_token:
        raise HTTPException(status_code=500, detail="Token generation failed")

    # Postman saves this in env var usually: {{accessToken}}
    return {"token": token_data.access_token}


@router.post("/logout")
def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    token = credentials.credentials

    # Delete the token row (revokes access + refresh because they�re in same row)
    deleted = (
        db.query(PersonalAccessToken)
        .filter(
            PersonalAccessToken.access_token == token,
            PersonalAccessToken.user_id == user_id,
        )
        .delete()
    )
    db.commit()

    # Optional behavior:
    # - If you want logout to error when token isn't found in DB, uncomment this.
    # if deleted == 0:
    #     raise HTTPException(status_code=401, detail="Token already revoked or not recognized")

    cache_manager.clear()

    return {"message": "Logged out successfully"}
