from pydantic import BaseModel, validator
from datetime import date, datetime
from typing import List, Optional

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

class ClothingItemBase(BaseModel):
    name: str
    brand: Optional[str] = None
    color: Optional[str] = None
    season: Optional[str] = None
    style: Optional[str] = None
    material: Optional[str] = None
    purchase_date: Optional[date] = None
    price: Optional[float] = None
    image_url: Optional[str] = None
    notes: Optional[str] = None
    category_id: int
    user_id: int

    @validator('purchase_date', pre=True)
    def empty_str_to_none(cls, v):
        if v == '' or v == 'null' or v == 'undefined':
            return None
        return v

class ClothingItemCreate(ClothingItemBase):
    tag_ids: Optional[List[int]] = []

class ClothingItem(ClothingItemBase):
    item_id: int
    created_at: datetime
    category: Optional[Category] = None
    tags: List[Tag] = []
    
    class Config:
        orm_mode = True

class CategoryWithClothes(Category):
    clothes: List[ClothingItem] = []