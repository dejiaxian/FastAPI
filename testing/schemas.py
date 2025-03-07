# Pydantic data models for data validation 
from pydantic import BaseModel, EmailStr
from typing import Optional

# Base schema for user data
class UserBase(BaseModel):
    name: str
    email: EmailStr  
    position: str  
    university: str  

# Schema for creating a new user
class UserCreate(UserBase):
    pass

# Schema for updating a user
class UserUpdate(BaseModel):
    name: Optional[str] = None
    position: Optional[str] = None
    university: Optional[str] = None

# Schema for returning user data
class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True  # Allows SQLAlchemy models to be returned as Pydantic models
