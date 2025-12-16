from pydantic import BaseModel

class UserCreate(BaseModel):
    name: str
    email: str
    address: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    address: str

    class Config:
        from_attributes = True
