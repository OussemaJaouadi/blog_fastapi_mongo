# schemas/common.py

from pydantic import BaseModel
from bson import ObjectId

class UserPopulate(BaseModel):
    id: str
    username: str

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class BlogPopulated(BaseModel):
    id: str
    title: str

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

