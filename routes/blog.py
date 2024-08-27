from typing import List
from fastapi import APIRouter, Depends, HTTPException
from schemas.blog import BlogCreate, BlogUpdate, BlogResponse
from services.blog import create_blog, get_all_blogs, get_blog_by_id, get_my_blogs, update_blog, delete_blog
from auth.handler import JWTBearer, get_jwt_subject
from db.connect import Database
from auth.utilities import TokenData

router = APIRouter(prefix="/blog", tags=["Blogs"])

def get_db():
    from main import database  # Avoid circular import
    return database

@router.post("/", response_model=BlogResponse, dependencies=[Depends(JWTBearer())])
async def create_blog_route(blog: BlogCreate, current_user: TokenData = Depends(get_jwt_subject), db: Database = Depends(get_db)):
    return await create_blog(blog, current_user, db)

@router.get("/", response_model=List[BlogResponse], dependencies=[Depends(JWTBearer())])
async def get_all_blogs_route(db: Database = Depends(get_db)):
    return await get_all_blogs(db)

@router.get("/me", response_model=List[BlogResponse], dependencies=[Depends(JWTBearer())])
async def get_my_blogs_route(current_user: TokenData = Depends(get_jwt_subject), db: Database = Depends(get_db)):
    return await get_my_blogs(current_user, db)

@router.get("/{blog_id}", response_model=BlogResponse, dependencies=[Depends(JWTBearer())])
async def get_blog_by_id_route(blog_id: str, db: Database = Depends(get_db)):
    return await get_blog_by_id(blog_id, db)

@router.put("/{blog_id}", response_model=BlogResponse, dependencies=[Depends(JWTBearer())])
async def update_blog_route(blog_id: str, blog_update: BlogUpdate, current_user: TokenData = Depends(get_jwt_subject), db: Database = Depends(get_db)):
    return await update_blog(blog_id, blog_update, current_user, db)

@router.delete("/{blog_id}", dependencies=[Depends(JWTBearer())])
async def delete_blog_route(blog_id: str, current_user: TokenData = Depends(get_jwt_subject), db: Database = Depends(get_db)):
    return await delete_blog(blog_id, current_user, db)
