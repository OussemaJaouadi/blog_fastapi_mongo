# schemas/blog.py

from typing import Optional
from pydantic import BaseModel, field_validator
from bson import ObjectId
from schemas.common import UserPopulate

class BlogCreate(BaseModel):
    title: str
    content: str

    @field_validator('title')
    def validate_title(cls, value):
        if not (6 <= len(value) <= 100):
            raise ValueError('Title must be between 6 and 100 characters long')
        if not all(c.isalnum() or c.isspace() or c == '_' for c in value):
            raise ValueError('Title can only contain alphanumeric characters, spaces, and underscores')
        return value

    @field_validator('content')
    def validate_content(cls, value):
        if not (1 <= len(value) <= 500):
            raise ValueError('Content must be between 1 and 500 characters long')
        if not all(c.isalnum() or c.isspace() or c in '.,!?()' for c in value):
            raise ValueError('Content contains invalid characters')
        return value

class BlogUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

    @field_validator('title')
    def validate_title(cls, value):
        if value is not None:
            if not (6 <= len(value) <= 100):
                raise ValueError('Title must be between 6 and 100 characters long')
            if not all(c.isalnum() or c.isspace() or c == '_' for c in value):
                raise ValueError('Title can only contain alphanumeric characters, spaces, and underscores')
        return value

    @field_validator('content')
    def validate_content(cls, value):
        if value is not None:
            if not (1 <= len(value) <= 500):
                raise ValueError('Content must be between 1 and 500 characters long')
            if not all(c.isalnum() or c.isspace() or c in '.,!?()' for c in value):
                raise ValueError('Content contains invalid characters')
        return value

class BlogResponse(BaseModel):
    id: str
    title: str
    content: str
    user: UserPopulate

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
