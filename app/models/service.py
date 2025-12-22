from sqlalchemy import String, Integer,Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db import Base

class Service(Base):
    __tablename__ = "services"
    __table_args__ = {"schema": "SWORD"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(Text, unique=False, nullable=True)