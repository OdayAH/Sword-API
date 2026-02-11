from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from starlette.authentication import AuthCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from app.db import get_db
from app.models.user import User
from app.models.roles import Role
from app.models.personal_access_token import PersonalAccessToken
from app.services.token_service import issue_and_store_tokens
from app.core.jwt import verify_token
from app.core.cache import cache_manager

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


def get_current_user(credentials = Depends(security)) -> int:

    return verify_token(credentials.credentials)


@router.get("/roles", response_model=list[RoleResponse])
def get_roles(db: Session = Depends(get_db)):
    roles = db.query(Role).order_by(Role.id).all()
    if not roles:
        raise HTTPException(status_code=500, detail="No roles found in database")
    return roles


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()

    if not user or user.password != payload.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token_data = issue_and_store_tokens(db, user)

    if not token_data or not token_data.access_token:
        raise HTTPException(status_code=500, detail="Token generation failed")

    return {"token": token_data.access_token}


@router.post("/logout")
def logout(
    credentials=Depends(security),
    db: Session = Depends(get_db),
):
    token = credentials.credentials

    user_id = verify_token(token)

    deleted = db.query(PersonalAccessToken).filter(
        PersonalAccessToken.access_token == token,
        PersonalAccessToken.user_id == user_id,
    ).delete()
    db.commit()

    cache_manager.clear()

    return {"message": "Logged out successfully"}
