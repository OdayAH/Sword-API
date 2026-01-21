from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db import get_db
from app.startup import init_db
from app.api.routers.users import router as users_router
from app.api.routers.addresses import router as addresses_router
from app.api.routers.services import router as services_router
from app.api.auth import router as auth_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/health/db")
def health_db(db: Session = Depends(get_db)):
    db.execute(select(1))
    return {"db": "ok"}

app.include_router(users_router)

app.include_router(addresses_router)

app.include_router(services_router)

app.include_router(auth_router)

