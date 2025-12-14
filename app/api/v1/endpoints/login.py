from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.mongodb import get_database
from app.core import security
from app.core.config import settings
from app.models.schemas.user import Token, UserCreate, UserInDB

router = APIRouter()


@router.post("/login/access-token", response_model=Token)
async def login_access_token(
        db: AsyncIOMotorDatabase = Depends(get_database),
        form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 兼容的 Token 登录接口，获取 Access Token
    """
    # 1. 查找用户
    user = await db["users"].find_one({"username": form_data.username})
    if not user:
        raise HTTPException(status_code=400, detail="用户名或密码错误")

    # 2. 验证密码
    if not security.verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=400, detail="用户名或密码错误")

    # 3. 生成 Token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user["username"], expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }


@router.post("/register", response_model=UserInDB)
async def register_user(
        user_in: UserCreate,
        db: AsyncIOMotorDatabase = Depends(get_database)
) -> Any:
    """
    注册新医生 (仅开发测试用，生产环境应由 Admin 创建)
    """
    user = await db["users"].find_one({"username": user_in.username})
    if user:
        raise HTTPException(status_code=400, detail="用户名已存在")

    user_doc = user_in.dict(exclude={"password"})
    user_doc["hashed_password"] = security.get_password_hash(user_in.password)
    user_doc["is_active"] = True

    result = await db["users"].insert_one(user_doc)

    return {
        "id": str(result.inserted_id),
        **user_doc
    }