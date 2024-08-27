# db/common.py

from pydantic import BaseModel
from bson.objectid import ObjectId
from enum import Enum

class RoleEnum(str, Enum):
    ADMIN = "ADMIN"
    USER = "USER"
