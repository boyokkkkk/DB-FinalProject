# 这个文件的作用是前端发数据过来时，后端先检查一遍格式对不对

from pydantic import BaseModel, Field
from typing import Optional, List
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

# ==================================================
# Outfit
# ==================================================
class ItemOut(BaseModel):
    item_id: int
    name: str
    category: str
    image_url: Optional[str] = None
    color: Optional[str] = None
    season: Optional[str] = None
    style: Optional[str] = None
    
    class Config:
        from_attributes = True

class OutfitItemCreate(BaseModel):
    item_id: int
    position_x: float = 0.0
    position_y: float = 0.0
    rotation: float = 0.0
    scale_x: float = 1.0
    scale_y: float = 1.0
    z_index: int = 0

class OutfitCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    season: Optional[str] = None
    style: Optional[str] = None
    image_url: Optional[str] = None # canvas image
    items: List[OutfitItemCreate] # items list

class OutfitItemDetailOut(BaseModel):
    item_id: int
    name: str
    category: str
    image_url: Optional[str] = None
    
    # Canvas info
    position_x: float
    position_y: float
    rotation: float
    scale_x: float
    scale_y: float
    z_index: int

    class Config:
        from_attributes = True

class OutfitDetailOut(BaseModel):
    outfit_id: int
    name: str
    description: Optional[str] = None
    season: Optional[str] = None
    style: Optional[str] = None
    image_url: Optional[str] = None
    create_time: datetime
    items: List[OutfitItemDetailOut] # items info&pos

    class Config:
        from_attributes = True
    
class OutfitOut(BaseModel):
    outfit_id: int
    name: str
    season: Optional[str] = None
    style: Optional[str] = None
    image_url: Optional[str] = None
    create_time: datetime
    # 可以添加一个字段表示包含多少件单品
    item_count: int

    class Config:
        from_attributes = True