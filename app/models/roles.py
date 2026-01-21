from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.db import Base

class Role(Base):
    __tablename__ = "roles"
    __table_args__ = {"schema": "SWORD"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)

