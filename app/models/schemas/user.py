from pydantic import BaseModel, EmailStr
from typing import Optional

# 共享的基础字段
class UserBase(BaseModel):
    username: str
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: str = "doctor"  # doctor, admin, researcher

# 创建用户时的字段 (需要密码)
class UserCreate(UserBase):
    password: str

# 数据库中读取的字段 (不返回密码)
class UserInDB(UserBase):
    id: str
    is_active: bool = True

# 登录成功返回的 Token 结构
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None