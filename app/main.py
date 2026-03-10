import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi.errors import RateLimitExceeded
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db import get_db
from app.startup import init_db
from app.api.routers.users import router as users_router
from app.api.routers.addresses import router as addresses_router
from app.api.routers.services import router as services_router
from app.api.routers.requests import router as requests_router
from app.api.auth import router as auth_router
from app.core.rate_limit import limiter, rate_limit_exceeded_handler

app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("uploads/profile_images", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

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

app.include_router(requests_router)

app.include_router(auth_router)

