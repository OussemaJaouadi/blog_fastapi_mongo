# auth/handlers.py

import logging.config
from typing import Optional, List
from bson import ObjectId
from fastapi import Request, HTTPException, Header, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timezone
from .utilities import decode_access_token
from db.common import RoleEnum
import logging
from db.connect import Database

logger = logging.getLogger(__name__)


def get_db():
    from main import database  # Avoid circular import
    return database

class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request,database: Database = Depends(get_db)):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
            token_status = await self.verify_jwt(credentials.credentials, database)
            if token_status == "invalid":
                raise HTTPException(status_code=403, detail="Invalid token.")
            elif token_status == "expired":
                raise HTTPException(status_code=403, detail="Expired token.")
            elif token_status == "user_not_found":
                raise HTTPException(status_code=403, detail="User not found.")
            return credentials.credentials
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

    async def verify_jwt(self, jwtoken: str,database: Database) -> str:
        try:
            payload = decode_access_token(jwtoken)
            user_collection = database.get_users_collection()
            user = await user_collection.find_one({"_id": ObjectId(payload.user_id)})
            if not user:
                return "user_not_found"
            expiration_time = datetime.fromisoformat(payload.expires_at)
            if datetime.now(timezone.utc) > expiration_time:
                return "expired"
            return "valid"
        except Exception as e:
            return "invalid"

async def get_jwt_subject(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header is missing")
    try:
        token = authorization.split()[1]
        payload = decode_access_token(token)
        return payload
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

async def verify_role(current_user: dict = Depends(get_jwt_subject), required_roles: List[RoleEnum] = []):
    if current_user["role"] not in required_roles:
        raise HTTPException(status_code=403, detail="You are not authorized to access this resource")
    return current_user
