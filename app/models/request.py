from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.service import Service

class Request(Base):
    __tablename__ = "requests"
    __table_args__ = {"schema": "SWORD"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("SWORD.users.id"), nullable=False)
    service_id: Mapped[int] = mapped_column(Integer, ForeignKey("SWORD.services.id"), nullable=False)

    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])
    service: Mapped["Service"] = relationship("Service", foreign_keys=[service_id])
