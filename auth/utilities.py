# auth/utilities

import jwt
from passlib.context import CryptContext
from pydantic import BaseModel, ValidationError
from datetime import datetime, timedelta, timezone
from config.config import settings
from bson import ObjectId
from db.common import RoleEnum

pwd_context = CryptContext(schemes=["bcrypt"], default="bcrypt")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)

class TokenData(BaseModel):
    user_id: str
    role: RoleEnum
    expires_at: str  # Change to string to handle serialization

    class Config:
        arbitrary_types_allowed = True

def create_access_token(user_id: ObjectId, role: RoleEnum, expires_delta: timedelta = timedelta(minutes=30)) -> str:
    expires_at = datetime.now(timezone.utc) + expires_delta
    # Convert ObjectId to string for the payload
    token_data = TokenData(user_id=str(user_id), role=role, expires_at=expires_at.isoformat())
    payload = token_data.model_dump()  # Use model_dump() to get the payload as a dictionary
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.ALGORITHM)

def decode_access_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.ALGORITHM])
        return TokenData(
            user_id=str(payload['user_id']),
            role=payload['role'],
            expires_at=payload['expires_at']
        )
    except (jwt.PyJWTError, ValidationError) as e:
        raise Exception(f"Invalid token: {str(e)}")

