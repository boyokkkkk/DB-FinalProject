# 这个文件的作用是前端发数据过来时，后端先检查一遍格式对不对

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# 注册登录
# 1. 基础模型：大家都有的字段
class UserBase(BaseModel):
    username: str
# 2. 注册时需要的字段 (前端 -> 后端)
class UserCreate(UserBase):
    password: str
# 3. 登录时需要的字段 (前端 -> 后端)
class UserLogin(UserBase):
    password: str
# 4. 返回给前端的用户信息 (后端 -> 前端)
# 注意：千万不能把 password 返回给前端！
class UserOut(UserBase):
    user_id: int
    avatar: Optional[str] = None
    create_time: datetime
    class Config:
        from_attributes = True # 允许从 SQLAlchemy 模型读取数据

# 更新用户信息时的校验模型
class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    avatar: Optional[str] = None