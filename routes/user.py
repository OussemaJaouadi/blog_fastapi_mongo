# routes/user.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from db.common import RoleEnum
from schemas.user import LoginRequest, LoginResponse, UserCreate, UserUpdate, UserResponse
from services.user import create_user, get_current_user, get_user, get_users, update_user, delete_user, authenticate_user
from auth.handler import JWTBearer, get_jwt_subject
from db.connect import Database

router = APIRouter(prefix="/user", tags=["Users"])

def get_db():
    from main import database  # Avoid circular import
    return database

@router.post("/register", response_model=UserResponse)
async def create_user_route(user: UserCreate, db: Database = Depends(get_db)):
    return await create_user(user, db)

@router.post("/login", response_model=LoginResponse)
async def authenticate_user_route(login_request: LoginRequest, db: Database = Depends(get_db)):
    return await authenticate_user(login_request.username, login_request.password, db)

@router.get("/", response_model=List[UserResponse], dependencies=[Depends(JWTBearer())])
async def get_users_route(db: Database = Depends(get_db), current_user: dict = Depends(get_jwt_subject)):
    return await get_users(db, current_user)

@router.get("/me", response_model=UserResponse,dependencies=[Depends(JWTBearer())])
async def get_current_user_route(current_user: dict = Depends(get_jwt_subject), db: Database = Depends(get_db)):
    return await get_current_user(current_user, db)

@router.get("/{user_id}", response_model=UserResponse,dependencies=[Depends(JWTBearer())])
async def get_user_route(user_id: str, current_user: dict = Depends(get_jwt_subject), db: Database = Depends(get_db)):
    return await get_user(user_id, db)


@router.put("/{user_id}", response_model=UserResponse,dependencies=[Depends(JWTBearer())])
async def update_user_route(user_id: str, user: UserUpdate, current_user: dict = Depends(get_jwt_subject), db: Database = Depends(get_db)):
    return await update_user(user_id, user, current_user, db)

@router.delete("/{user_id}",dependencies=[Depends(JWTBearer())])
async def delete_user_route(user_id: str, current_user: dict = Depends(get_jwt_subject), db: Database = Depends(get_db)):
    return await delete_user(user_id, current_user, db)
