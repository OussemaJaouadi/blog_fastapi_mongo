from fastapi import HTTPException
from bson import ObjectId
from db.common import RoleEnum
from db.connect import Database
from schemas.user import LoginResponse, UserCreate, UserUpdate, UserResponse
from schemas.common import BlogPopulated
from auth.utilities import TokenData, create_access_token, hash_password, verify_password
from motor.motor_asyncio import AsyncIOMotorCollection

async def get_user_blogs(user_id: str, db: Database) -> list[BlogPopulated]:
    blogs_collection: AsyncIOMotorCollection = db.get_blogs_collection()
    user_blogs_cursor = blogs_collection.find({"user_id": ObjectId(user_id)})
    user_blogs = await user_blogs_cursor.to_list(length=None)
    return [BlogPopulated(id=str(blog["_id"]), title=blog["title"]) for blog in user_blogs]

async def create_user(user: UserCreate, db: Database):
    users_collection: AsyncIOMotorCollection = db.get_users_collection()
    existing_user = await users_collection.find_one({"$or": [{"username": user.username}, {"email": user.email}]})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already exists")

    user_dict = {
        "username": user.username,
        "email": user.email,
        "password": hash_password(user.password),
        "role": RoleEnum.USER
    }
    new_user = await users_collection.insert_one(user_dict)
    created_user = await users_collection.find_one({"_id": new_user.inserted_id})
    if created_user:
        user_blogs = await get_user_blogs(str(created_user["_id"]), db)
        return UserResponse(
            id=str(created_user["_id"]),
            username=created_user["username"],
            email=created_user["email"],
            blogs=user_blogs
        )
    else:
        raise HTTPException(status_code=500, detail="Failed to create user")

async def get_user(user_id: str, db: Database):
    users_collection: AsyncIOMotorCollection = db.get_users_collection()
    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if user:
        user_blogs = await get_user_blogs(user_id, db)
        return UserResponse(
            id=str(user["_id"]),
            username=user["username"],
            email=user["email"],
            blogs=user_blogs
        )
    else:
        raise HTTPException(status_code=404, detail="User not found")

async def get_users(db: Database, current_user: TokenData):

    users_collection: AsyncIOMotorCollection = db.get_users_collection()
    users_cursor = users_collection.find()
    result = []
    async for user in users_cursor:
        user_blogs = await get_user_blogs(str(user["_id"]), db)
        result.append(
            UserResponse(
                id=str(user["_id"]),
                username=user["username"],
                email=user["email"],
                blogs=user_blogs
            )
        )
    return result

async def update_user(user_id: str, user: UserUpdate, current_user: TokenData, db: Database):
    if user_id != str(current_user.user_id) and current_user.role != RoleEnum.ADMIN:
        raise HTTPException(status_code=403, detail="You are not authorized to update this user")

    update_data = user.model_dump(exclude_unset=True)  # Use model_dump to get the dict
    if "password" in update_data and update_data["password"]:
        update_data["password"] = hash_password(update_data["password"])

    users_collection: AsyncIOMotorCollection = db.get_users_collection()
    updated_user = await users_collection.find_one_and_update(
        {"_id": ObjectId(user_id)},
        {"$set": update_data},
        return_document=True
    )

    if updated_user:
        user_blogs = await get_user_blogs(user_id, db)
        return UserResponse(
            id=str(updated_user["_id"]),
            username=updated_user["username"],
            email=updated_user["email"],
            blogs=user_blogs
        )
    else:
        raise HTTPException(status_code=404, detail="User not found")

async def delete_user(user_id: str, current_user: TokenData, db: Database):
    if user_id != str(current_user.user_id) and current_user.role != RoleEnum.ADMIN:
        raise HTTPException(status_code=403, detail="You are not authorized to delete this user")

    users_collection: AsyncIOMotorCollection = db.get_users_collection()
    result = await users_collection.delete_one({"_id": ObjectId(user_id)})
    if result.deleted_count == 1:
        return {"message": "User deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="User not found")

async def authenticate_user(username: str, password: str, db: Database):
    users_collection: AsyncIOMotorCollection = db.get_users_collection()
    user = await users_collection.find_one({"username": username})
    if user and verify_password(password, user["password"]):
        token = create_access_token(user['_id'], user['role'])
        return LoginResponse(access_token=token)
    else:
        raise HTTPException(status_code=401, detail="Invalid username or password")

async def get_current_user(user: TokenData, db: Database) -> UserResponse:
    user_id = user.user_id
    users_collection: AsyncIOMotorCollection = db.get_users_collection()
    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if user:
        user_blogs = await get_user_blogs(user_id, db)
        return UserResponse(
            id=str(user["_id"]),
            username=user["username"],
            email=user["email"],
            blogs=user_blogs
        )
    else:
        raise HTTPException(status_code=404, detail="User not found")
