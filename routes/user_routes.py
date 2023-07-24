from bson import ObjectId
from fastapi import APIRouter, HTTPException

from config.database import col_user
from models.user_model import User
from schemas.user_schema import users_serializer

user_router = APIRouter()


@user_router.post("/users")
async def create_user(user: User):
    _id = col_user.insert_one(dict(user))
    user_data = users_serializer(col_user.find({"_id": _id.inserted_id}))
    return {"status": "Ok", "data": user_data}


@user_router.get("/users")
async def find_all_users():
    users = users_serializer(col_user.find())
    return {"status": "Ok", "data": users}


@user_router.get("/users/{id}")
async def get_one_user(id: str):
    user = users_serializer(col_user.find({"_id": ObjectId(id)}))
    return {"status": "Ok", "data": user}


@user_router.put("/users/{id}")
async def update_user(id: str, user: User):
    col_user.find_one_and_update(
        {
            "_id": ObjectId(id)
        },
        {
            "$set": dict(user)
        })
    user = users_serializer(col_user.find({"_id": ObjectId(id)}))
    return {"status": "Ok", "data": user}


@user_router.delete("/users/{id}")
async def delete_user(id: str):
    user_delete = users_serializer(col_user.find({"_id": ObjectId(id)}))
    if len(user_delete) == 1:
        data = user_delete[0]
        col_user.delete_one({"_id": ObjectId(id)})
        # users = users_serializer(col_user.find())
        return {"status": "Ok", "Data_deleted": data}
    raise HTTPException(status_code=404, detail="User not found")
