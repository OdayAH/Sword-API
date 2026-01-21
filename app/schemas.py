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

    class Config:
        from_attributes = True


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
    def validate_not_empty(cls, v: str):
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
    def validate_not_empty(cls, v: Optional[str]):
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("This field cannot be empty")
            return v
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

    class Config:
        from_attributes = True

class ServiceCreate(BaseModel):
    name: str
    description: str
    price: int
    status: bool = True

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str):
        v = v.strip()
        if not v:
            raise ValueError("Name cannot be empty")
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str):
        v = v.strip()
        if not v:
            raise ValueError("Description cannot be empty")
        return v

    @field_validator("price", mode="before")
    @classmethod
    def validate_price(cls, v):
        if isinstance(v, str):
            try:
                v = int(v)
            except ValueError:
                raise ValueError("Price must be a valid integer")
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
    def validate_name(cls, v: Optional[str]):
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("Name cannot be empty")
            return v
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: Optional[str]):
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("Description cannot be empty")
            return v
        return v

    @field_validator("price")
    @classmethod
    def validate_price(cls, v: Optional[int]):
        if v is not None and v <= 0:
            raise ValueError("Price must be greater than 0")
        return v


class ServiceResponse(BaseModel):
    id: int
    name: str
    description: str
    price: int
    status: bool
    provider_id: int
    provider: Optional[dict] = None

    class Config:
        from_attributes = True

