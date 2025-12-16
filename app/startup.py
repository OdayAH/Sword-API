from app.db import Base, engine
from app.models.user import User
from app.models.service import Service 

def init_db() -> None:
    Base.metadata.create_all(bind=engine)
