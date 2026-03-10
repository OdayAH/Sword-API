from datetime import date
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.user import User
from app.schemas import UserCreate, UserResponse, UserUpdate
from app.services.token_service import issue_and_store_tokens
from app.core.security import get_current_user

router = APIRouter(prefix="/users", tags=["users"])

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_FILE_SIZE = 2 * 1024 * 1024  # 2 MB
UPLOAD_DIR = Path("uploads/profile_images")


def _build_user_response(user: User, token: str | None = None) -> UserResponse:
    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        date_of_birth=user.date_of_birth,
        phone=user.phone,
        website=user.website,
        profile_image=user.profile_image,
        role={"id": user.role.id, "name": user.role.name} if user.role else None,
        token=token,
    )


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return _build_user_response(current_user)


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
            website=user.website,
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        token_data = issue_and_store_tokens(db, new_user)
        access_token = token_data.access_token if token_data else None

        return _build_user_response(new_user, token=access_token)

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

    return _build_user_response(current_user)


@router.post("/me/profile-image", response_model=UserResponse)
async def upload_profile_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Upload or replace the current user's profile picture.

    Restrictions:
    - Allowed types: JPEG, PNG, WebP
    - Max size: 2 MB
    """
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{file.content_type}'. Allowed: JPEG, PNG, WebP.",
        )

    ext = Path(file.filename).suffix.lower() if file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file extension '{ext}'. Allowed: .jpg, .jpeg, .png, .webp.",
        )

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="File size exceeds the 2 MB limit.",
        )

    # Delete old image from disk if present
    if current_user.profile_image:
        old_path = UPLOAD_DIR / current_user.profile_image
        if old_path.exists():
            old_path.unlink()

    # Build a unique filename:  <original_stem>_<YYYY-MM-DD><ext>
    original_stem = Path(file.filename).stem
    today = date.today().isoformat()          # e.g. "2026-03-02"
    unique_name = f"{original_stem}_{today}{ext}"
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    (UPLOAD_DIR / unique_name).write_bytes(content)

    current_user.profile_image = unique_name
    db.commit()
    db.refresh(current_user)

    return _build_user_response(current_user)


@router.delete("/me/profile-image", status_code=status.HTTP_204_NO_CONTENT)
def delete_profile_image(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Remove the current user's profile picture."""
    if not current_user.profile_image:
        raise HTTPException(status_code=404, detail="No profile image to delete.")

    old_path = UPLOAD_DIR / current_user.profile_image
    if old_path.exists():
        old_path.unlink()

    current_user.profile_image = None
    db.commit()


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_current_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Clean up profile image from disk before deleting the user
    if current_user.profile_image:
        old_path = UPLOAD_DIR / current_user.profile_image
        if old_path.exists():
            old_path.unlink()

    for token in current_user.personal_access_tokens:
        db.delete(token)

    db.delete(current_user)
    db.commit()
