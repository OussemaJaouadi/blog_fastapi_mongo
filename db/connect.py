# db/connect.py

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.collection import Collection
from typing import Optional
from config.config import settings

class Database:
    def __init__(self):
        self.db = AsyncIOMotorClient(settings.DB_URL, username=settings.DB_USER, password=settings.DB_PASS)[settings.DB_NAME]
    
    def get_users_collection(self) -> Collection:
        return self.db.users

    def get_blogs_collection(self) -> Collection:
        return self.db.blogs

