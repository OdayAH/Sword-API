from pydantic import BaseModel

class UserCreate(BaseModel):
    name: str
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    name: str

    

    class Config:
        from_attributes = True
