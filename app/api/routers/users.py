from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.user import User
from app.models.roles import Role
from app.schemas import UserCreate, UserResponse, UserUpdate
from app.services.token_service import issue_and_store_tokens
from app.core.security import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        date_of_birth=current_user.date_of_birth,
        phone=current_user.phone,
        website=current_user.website,
        role={"id": current_user.role.id, "name": current_user.role.name} if current_user.role else None,
        token=None,
    )


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user with selected role (1=user, 2=provider)."""
    try:
        if db.query(User).filter(User.email == user.email).first():
            raise HTTPException(status_code=409, detail="Email already exists")

        if user.role_id not in [1, 2]:
            raise HTTPException(status_code=400, detail="Invalid role. Must be 1 (user) or 2 (provider)")

        new_user = User(
            name=user.name,
            email=user.email,
            password=user.password,
            date_of_birth=user.date_of_birth,
            phone=user.phone,
            role_id=user.role_id,
            website=user.website
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        token_data = issue_and_store_tokens(db, new_user)
        access_token = token_data.access_token if token_data else None

        return UserResponse(
            id=new_user.id,
            name=new_user.name,
            email=new_user.email,
            date_of_birth=new_user.date_of_birth,
            phone=new_user.phone,
            website=new_user.website,
            role={"id": new_user.role.id, "name": new_user.role.name} if new_user.role else None,
            token=access_token
        )

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")


@router.put("/me", response_model=UserResponse)
def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update the current authenticated user's profile using bearer token."""
    data = user_update.model_dump(exclude_unset=True)
    data.pop("email", None)

    for field, value in data.items():
        setattr(current_user, field, value)

    db.commit()
    db.refresh(current_user)

    return UserResponse(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        date_of_birth=current_user.date_of_birth,
        phone=current_user.phone,
        website=current_user.website,
        role={"id": current_user.role.id, "name": current_user.role.name} if current_user.role else None,
        token=None,
    )


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_current_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    for token in current_user.personal_access_tokens:
        db.delete(token)

    db.delete(current_user)
    db.commit()
