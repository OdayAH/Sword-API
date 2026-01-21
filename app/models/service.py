from sqlalchemy import String, Integer, Text, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User

class Service(Base):
    __tablename__ = "services"
    __table_args__ = {"schema": "SWORD"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False, unique=False)
    description: Mapped[str] = mapped_column(Text, unique=False, nullable=False)
    price: Mapped[int] = mapped_column(Integer, unique=False, nullable=False)
    status: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    provider_id: Mapped[int] = mapped_column(Integer, ForeignKey("SWORD.users.id"), nullable=False)
    
    provider: Mapped["User"] = relationship("User", foreign_keys=[provider_id])
    