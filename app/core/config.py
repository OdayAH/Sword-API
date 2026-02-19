import os
from dotenv import load_dotenv

load_dotenv() 

DATABASE_URL = os.environ["DATABASE_URL"]

JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"]
JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM", "HS256")

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"])
REFRESH_TOKEN_EXPIRE_DAYS = int(os.environ["REFRESH_TOKEN_EXPIRE_DAYS"])

MAILTRAP_HOST = os.environ.get("MAILTRAP_HOST", "sandbox.smtp.mailtrap.io")
MAILTRAP_PORT = int(os.environ.get("MAILTRAP_PORT", "2525"))
MAILTRAP_USERNAME = os.environ["MAILTRAP_USERNAME"]
MAILTRAP_PASSWORD = os.environ["MAILTRAP_PASSWORD"]
MAIL_FROM = os.environ.get("MAIL_FROM", "SWORD <noreply@sword.com>")
