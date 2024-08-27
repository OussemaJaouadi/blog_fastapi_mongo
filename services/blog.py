from typing import List
from fastapi import HTTPException
from bson import ObjectId
from db.common import RoleEnum
from db.connect import Database
from schemas.blog import BlogCreate, BlogUpdate, BlogResponse
from schemas.common import UserPopulate
from auth.utilities import TokenData
from motor.motor_asyncio import AsyncIOMotorCollection

async def get_user_by_id(user_id: str, db: Database) -> UserPopulate:
    users_collection = db.get_users_collection()
    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if user:
        return UserPopulate(
            id=str(user["_id"]),
            username=user["username"]
        )
    return None

async def create_blog(blog: BlogCreate, current_user: TokenData, db: Database) -> BlogResponse:
    blogs_collection: AsyncIOMotorCollection = db.get_blogs_collection()
    blog_dict = {
        "title": blog.title,
        "content": blog.content,
        "user_id": current_user.user_id
    }
    new_blog = await blogs_collection.insert_one(blog_dict)
    created_blog = await blogs_collection.find_one({"_id": new_blog.inserted_id})
    user_info = await get_user_by_id(created_blog["user_id"], db)
    
    return BlogResponse(
        id=str(created_blog["_id"]),
        title=created_blog["title"],
        content=created_blog["content"],
        user=user_info
    )

async def get_all_blogs(db: Database) -> List[BlogResponse]:
    blogs_collection: AsyncIOMotorCollection = db.get_blogs_collection()
    blogs_cursor = blogs_collection.find()
    result = []
    async for blog in blogs_cursor:
        user_info = await get_user_by_id(blog["user_id"], db)
        result.append(
            BlogResponse(
                id=str(blog["_id"]),
                title=blog["title"],
                content=blog["content"],
                user=user_info
            )
        )
    return result

async def get_blog_by_id(blog_id: str, db: Database) -> BlogResponse:
    blogs_collection: AsyncIOMotorCollection = db.get_blogs_collection()
    blog = await blogs_collection.find_one({"_id": ObjectId(blog_id)})
    if blog:
        user_info = await get_user_by_id(blog["user_id"], db)
        return BlogResponse(
            id=str(blog["_id"]),
            title=blog["title"],
            content=blog["content"],
            user=user_info
        )
    else:
        raise HTTPException(status_code=404, detail="Blog not found")

async def get_my_blogs(current_user: TokenData, db: Database) -> List[BlogResponse]:
    blogs_collection: AsyncIOMotorCollection = db.get_blogs_collection()
    user_blogs_cursor = blogs_collection.find({"user_id": current_user.user_id})
    result = []
    async for blog in user_blogs_cursor:
        user_info = await get_user_by_id(blog["user_id"], db)
        result.append(
            BlogResponse(
                id=str(blog["_id"]),
                title=blog["title"],
                content=blog["content"],
                user=user_info
            )
        )
    return result

async def update_blog(blog_id: str, blog_update: BlogUpdate, current_user: TokenData, db: Database) -> BlogResponse:
    blogs_collection: AsyncIOMotorCollection = db.get_blogs_collection()
    blog = await blogs_collection.find_one({"_id": ObjectId(blog_id)})
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")
    
    if blog["user_id"] != current_user.user_id and current_user.role != RoleEnum.ADMIN:
        raise HTTPException(status_code=403, detail="You are not authorized to update this blog")

    update_data = blog_update.dict(exclude_unset=True)
    updated_blog = await blogs_collection.find_one_and_update(
        {"_id": ObjectId(blog_id)},
        {"$set": update_data},
        return_document=True
    )
    user_info = await get_user_by_id(updated_blog["user_id"], db)
    
    return BlogResponse(
        id=str(updated_blog["_id"]),
        title=updated_blog["title"],
        content=updated_blog["content"],
        user=user_info
    )

async def delete_blog(blog_id: str, current_user: TokenData, db: Database):
    blogs_collection: AsyncIOMotorCollection = db.get_blogs_collection()
    blog = await blogs_collection.find_one({"_id": ObjectId(blog_id)})
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")

    if blog["user_id"] != current_user.user_id and current_user.role != RoleEnum.ADMIN:
        raise HTTPException(status_code=403, detail="You are not authorized to delete this blog")

    result = await blogs_collection.delete_one({"_id": ObjectId(blog_id)})
    if result.deleted_count == 1:
        return {"message": "Blog deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Failed to delete blog")
