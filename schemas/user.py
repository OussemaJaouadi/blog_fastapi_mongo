# schemas/user.py

from typing import List, Optional
from pydantic import BaseModel, EmailStr, field_validator
from bson import ObjectId
from db.common import RoleEnum
from schemas.common import BlogPopulated

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

    @field_validator('username')
    def validate_username(cls, value):
        if not (6 <= len(value) <= 50):
            raise ValueError('Username must be between 6 and 50 characters long')
        if not all(c.isalnum() or c.isspace() or c == '_' for c in value):
            raise ValueError('Username can only contain alphanumeric characters, spaces, and underscores')
        return value

class UserUpdate(BaseModel):
    username: Optional[str] = None

    @field_validator('username')
    def validate_username(cls, value):
        if value is not None:
            if not (6 <= len(value) <= 50):
                raise ValueError('Username must be between 6 and 50 characters long')
            if not all(c.isalnum() or c.isspace() or c == '_' for c in value):
                raise ValueError('Username can only contain alphanumeric characters, spaces, and underscores')
        return value

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    blogs: List[BlogPopulated] = []

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class LoginResponse(BaseModel):
    access_token: str = None
    
    class Config:
        arbitrary_types_allowed = True

class LoginRequest(BaseModel):
    username: str
    password: str