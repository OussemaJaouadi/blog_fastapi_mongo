# db/blog.py

from bson.objectid import ObjectId
from pydantic import BaseModel, Field, field_validator, validator
from db.common import PyObjectId

class Blog(BaseModel):
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    title: str
    content: str
    user_id: str

    @field_validator('id', 'user_id', pre=True)
    def validate_object_id(cls, value):
        if not ObjectId.is_valid(value):
            raise ValueError("Invalid ObjectId")
        return value

    class Config:
        json_encoders = {ObjectId: str}


