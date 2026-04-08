from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()

@router.post("/login/access-token")
async def login_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # TODO: 替换为实际的 MongoDB 查库和密码校验逻辑
    if form_data.username == "admin" and form_data.password == "admin":
        return {"access_token": "fake-jwt-token", "token_type": "bearer"}
    raise HTTPException(status_code=400, detail="用户名或密码错误")

@router.post("/register")
async def register_user(user_in: dict):
    # TODO: 将新医生/用户写入 MongoDB
    return {"msg": "用户注册成功", "user": user_in}