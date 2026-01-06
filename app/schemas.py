from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
import re
from datetime import date


class UserCreate(BaseModel):
    name: str
    date_of_birth: date
    phone: str
    email: EmailStr
    password: str


    @field_validator("name")
    @classmethod
    def validate_name(cls, name: str):
         name = name.strip()
         if not name:
            raise ValueError("Name cannot be empty")
         return name    
    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str):
        v = v.strip()
        if not v:
            raise ValueError("Phone cannot be empty")
        if not re.fullmatch(r"\d{7,15}", v):
            raise ValueError("Phone must be 7–15 digits")
        return v
    
    @field_validator("date_of_birth")
    @classmethod
    def validate_age(cls, v: date):
        today = date.today()

        age = today.year - v.year - (
        (today.month, today.day) < (v.month, v.day)
        )

        if age < 18:
            raise ValueError("You must be at least 18 years old")

        return v



    @field_validator("password")
    @classmethod
    def validate_password(cls, password: str):
        password = password.strip()

        if not password:
            raise ValueError("Password cannot be empty")
    
        if " " in password:
            raise ValueError("Password cannot contain spaces")

        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters")

        if not re.search(r"[A-Z]", password):
            raise ValueError("Password must contain at least one capital letter")

        if not re.search(r"[0-9]", password):
            raise ValueError("Password must contain at least one number")

        if not re.search(r"[^a-zA-Z0-9]", password):
            raise ValueError("Password must contain at least one special character")

        return password

class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    date_of_birth: date
    phone: str
    token: Optional[str] = None

    class Config:
        from_attributes = True
