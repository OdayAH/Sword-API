from __future__ import annotations

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
    role_id: int = 1
    website: Optional[str] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, name: str) -> str:
        name = name.strip()
        if not name:
            raise ValueError("Name cannot be empty")
        return name

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        v = v.strip()
        if not re.fullmatch(r"\d{7,15}", v):
            raise ValueError("Phone must be 7–15 digits")
        return v

    @field_validator("date_of_birth")
    @classmethod
    def validate_date_of_birth(cls, v: date) -> date:
        today = date.today()
        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
        if age < 18:
            raise ValueError("You must be at least 18 years old")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, password: str) -> str:
        password = password.strip()
        if len(password) < 8 or " " in password or not re.search(r"[A-Z]", password) or not re.search(r"[0-9]", password) or not re.search(r"[^a-zA-Z0-9]", password):
            raise ValueError("Password must be at least 8 characters, contain at least one capital letter, one number, and one special character")
        return password


class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    website: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    date_of_birth: date
    phone: str
    website: Optional[str] = None
    role: Optional[dict] = None
    token: Optional[str] = None

    model_config = {"from_attributes": True}


class AddressCreate(BaseModel):
    country: str
    city: str
    street: str
    building: str
    floor: str
    nickname: str
    is_default: bool = False

    @field_validator("country", "city", "street", "building", "floor", "nickname")
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("This field cannot be empty")
        return v


class AddressUpdate(BaseModel):
    country: Optional[str] = None
    city: Optional[str] = None
    street: Optional[str] = None
    building: Optional[str] = None
    floor: Optional[str] = None
    nickname: Optional[str] = None
    is_default: Optional[bool] = None

    @field_validator("country", "city", "street", "building", "floor", "nickname")
    @classmethod
    def validate_not_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("This field cannot be empty")
        return v


class AddressResponse(BaseModel):
    id: int
    user_id: int
    country: str
    city: str
    street: str
    building: str
    floor: str
    nickname: str
    is_default: bool

    model_config = {"from_attributes": True}


class ServiceCreate(BaseModel):
    name: str
    description: str
    price: int
    status: bool = True

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Name cannot be empty")
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Description cannot be empty")
        return v

    @field_validator("price", mode="before")
    @classmethod
    def validate_price(cls, v) -> int:
        if isinstance(v, str):
            if not v.isdigit():
                raise ValueError("Price must be a valid integer")
            v = int(v)
        if v <= 0:
            raise ValueError("Price must be greater than 0")
        return v


class ServiceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[int] = None
    status: Optional[bool] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("Name cannot be empty")
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("Description cannot be empty")
        return v

    @field_validator("price")
    @classmethod
    def validate_price(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v <= 0:
            raise ValueError("Price must be greater than 0")
        return v


class ServiceResponse(BaseModel):
    id: int
    name: str
    description: str
    price: int
    status: bool
    provider: Optional[dict] = None

    model_config = {"from_attributes": True}

