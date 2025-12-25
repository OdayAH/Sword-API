from fastapi import FastAPI, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db import get_db
from app.startup import init_db
from app.api.routes import router 
from app.api.routers.users import router as users_router

app = FastAPI()

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/health/db")
def health_db(db: Session = Depends(get_db)):
    db.execute(select(1))
    return {"db": "ok"}

app.include_router(users_router)
