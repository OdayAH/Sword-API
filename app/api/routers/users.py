from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.user import User
from app.schemas import UserCreate, UserResponse
from app.services.token_service import issue_and_store_tokens

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserResponse])
def get_all_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [UserResponse(id=u.id, name=u.name, email=u.email, token=None) for u in users]


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(id=user.id, name=user.name, email=user.email, token=None)


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        if db.query(User).filter(User.email == user.email).first():
            raise HTTPException(status_code=409, detail="Email already exists")

        new_user = User(**user.model_dump())
        db.add(new_user)
        db.commit()
        db.refresh(new_user) 
        # Generate and store token
        token_data = issue_and_store_tokens(db, new_user)
        
        # Ensure we have the access token
        access_token = token_data.access_token if token_data else None
        
        # Return user response with token
        response = UserResponse(
            id=new_user.id,
            name=new_user.name,
            email=new_user.email,
            token=access_token
        )
        
        return response
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")


@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    for field, value in user.model_dump().items():
        setattr(db_user, field, value)

    db.commit()
    db.refresh(db_user)
    return UserResponse(id=db_user.id, name=db_user.name, email=db_user.email, token=None)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Delete all related personal access tokens first
    for token in db_user.personal_access_tokens:
        db.delete(token)
    
    # Now delete the user
    db.delete(db_user)
    db.commit()
