# app/models/user.py
from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Date, ForeignKey
from app.db import Base
from app.models.personal_access_token import PersonalAccessToken
from app.models.address import Address

if TYPE_CHECKING:
    from app.models.roles import Role

class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "SWORD"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(150), nullable=False)
    date_of_birth: Mapped[Date] = mapped_column(Date, nullable=False)
    phone: Mapped[str] = mapped_column(String(15), nullable=True)
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey("SWORD.roles.id"), nullable=False, server_default="1")
    website: Mapped[str] = mapped_column(String(150), unique=False, nullable=True)

    role: Mapped[Role] = relationship("Role")

    personal_access_tokens: Mapped[list[PersonalAccessToken]] = relationship(
        "PersonalAccessToken",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    addresses: Mapped[list[Address]] = relationship(
        "Address",
        back_populates="user",
        cascade="all, delete-orphan",
    )
