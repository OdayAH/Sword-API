from app.db import Base, engine
import app.models  # noqa: F401  # loads models via app/models/__init__.py

def init_db() -> None:
    Base.metadata.create_all(bind=engine)
