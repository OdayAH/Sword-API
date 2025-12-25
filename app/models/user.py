# app/models/user.py
from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String
from app.db import Base

if TYPE_CHECKING:
    from app.models.personal_access_token import PersonalAccessToken

class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "SWORD"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(150), nullable=False)

    personal_access_tokens: Mapped[list[PersonalAccessToken]] = relationship(
        "PersonalAccessToken",
        back_populates="user",
        cascade="all, delete-orphan",
    )
