from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime, date

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

class TagBase(BaseModel):
    tag_name: str
    tag_type: str

class TagCreate(TagBase):
    pass

class Tag(TagBase):
    tag_id: int
    
    class Config:
        orm_mode = True

class CategoryBase(BaseModel):
    category_name: str
    category_type: str

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    category_id: int
    item_count: Optional[int] = 0
    
    class Config:
        orm_mode = True


# 拆分：前端提交用的基础模型（无 user_id）
class ClothingItemCreateBase(BaseModel):
    name: str
    brand: Optional[str] = None
    color: Optional[str] = None
    season: Optional[str] = None
    occasion: Optional[str] = None
    style: Optional[str] = None
    material: Optional[str] = None
    purchase_date: Optional[date] = None
    price: Optional[float] = None
    image_url: Optional[str] = None
    notes: Optional[str] = None
    category_id: int

    @validator('purchase_date', pre=True)
    def empty_str_to_none(cls, v):
        if v == '' or v == 'null' or v == 'undefined':
            return None
        return v


# 前端提交的创建模型（仅继承无 user_id 的基类）
class ClothingItemCreate(ClothingItemCreateBase):
    tag_ids: Optional[List[int]] = []


# 数据库/返回前端的基础模型（包含 user_id）
class ClothingItemBase(ClothingItemCreateBase):
    user_id: int  # 仅在返回/数据库模型中包含 user_id


# 最终返回给前端的衣物模型
class ClothingItem(ClothingItemBase):
    item_id: int
    created_at: datetime
    category: Optional[Category] = None
    tags: List[Tag] = []

    class Config:
        orm_mode = True

class CategoryWithClothes(Category):
    clothes: List[ClothingItem] = []
