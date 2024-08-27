# db/user

from typing import List
from bson.objectid import ObjectId
from pydantic import BaseModel, EmailStr, Field
from db.common import  RoleEnum

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    username: str
    email: EmailStr
    password: str
    role: RoleEnum
    blogs: List[str] = Field(default_factory=list)

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
