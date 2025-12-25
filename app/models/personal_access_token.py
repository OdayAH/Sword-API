# app/models/personal_access_token.py
from __future__ import annotations
from typing import TYPE_CHECKING
from datetime import datetime
from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

if TYPE_CHECKING:
    from app.models.user import User

class PersonalAccessToken(Base):
    __tablename__ = "personal_access_tokens"
    __table_args__ = {"schema": "SWORD"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("SWORD.users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    access_token: Mapped[str] = mapped_column(String(1024), nullable=False, unique=True)
    refresh_token: Mapped[str] = mapped_column(String(1024), nullable=False, unique=True)

    access_expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    refresh_expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    user: Mapped[User] = relationship("User", back_populates="personal_access_tokens")
