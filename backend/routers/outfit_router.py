from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
import os

from database import get_db
import models
import schemas
import security

router = APIRouter(
    prefix="/api/outfits",
    tags=["Outfits & Items"],
)

# ==========================================
# 1. 获取用户的单品列表 (OutfitStudio 左侧)
# ==========================================
@router.get("/items") # 这里的 response_model 稍微复杂，因为我们需要 category 信息来做前端分类
def get_user_items(
    db: Session = Depends(get_db),
    user_id: int = Depends(security.get_current_user_id)
):
    """
    获取当前用户衣橱中所有的单品列表。
    前端 OutfitBoard.vue 需要根据 category 分组 ('Top', 'Bottom' 等)。
    因此我们这里最好把 category_type 或者 category_name 返回去。
    """
    # 联表查询：ClothingItem + Category
    items = (
        db.query(models.ClothingItem, models.Category.category_type, models.Category.category_name)
        .join(models.Category, models.ClothingItem.category_id == models.Category.category_id)
        .filter(models.ClothingItem.user_id == user_id)
        .all()
    )

    result = []
    for item, cat_type, cat_name in items:
        raw_cat = cat_type if cat_type else "Other"
        display_cat = raw_cat.capitalize()
        
        result.append({
            "item_id": item.item_id,
            "name": item.name,
            "image_url": item.image_url,
            "category": display_cat,
            "original_category": cat_name
        })

    return result

# ==========================================
# 2. 创建/保存一个搭配
# ==========================================
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_outfit(
    outfit_data: schemas.OutfitCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(security.get_current_user_id)
):
    if not outfit_data.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="搭配必须包含至少一件单品"
        )
    
    new_outfit = models.Outfit(
        user_id=user_id,
        name=outfit_data.name,
        description=outfit_data.description,
        season=outfit_data.season,
        style=outfit_data.style,
        image_url=outfit_data.image_url,
        meta_data=outfit_data.meta_data
    )
    db.add(new_outfit)
    db.commit()
    db.refresh(new_outfit)
    
    outfit_refs = []
    for item_data in outfit_data.items:
        outfit_ref = models.OutfitRef(
            outfit_id=new_outfit.outfit_id,
            item_id=item_data.item_id,
            position_x=item_data.position_x,
            position_y=item_data.position_y,
            rotation=item_data.rotation,
            scale_x=item_data.scale_x,
            scale_y=item_data.scale_y,
            z_index=item_data.z_index,
        )
        outfit_refs.append(outfit_ref)
    
    db.add_all(outfit_refs)
    db.commit()
    
    return {"message": "搭配创建成功", "outfit_id": new_outfit.outfit_id}

def delete_local_file(image_url: str):
    if not image_url:
        return
    
    # 只处理本地 static 目录下的文件
    if image_url.startswith("/static/"):
        try:
            # 去掉开头的 /，拼接成相对路径 (假设运行目录在项目根目录)
            # 例如: /static/uploads/outfits/abc.jpg -> static/uploads/outfits/abc.jpg
            file_path = image_url.lstrip("/")
            
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"已删除旧图片: {file_path}")
        except Exception as e:
            print(f"删除图片失败: {e}")

@router.put("/{outfit_id}")
def update_outfit(
    outfit_id: int,
    outfit_update: schemas.OutfitUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(security.get_current_user_id)
):
    # 1. 查找现有搭配
    outfit = db.query(models.Outfit).filter(models.Outfit.outfit_id == outfit_id, models.Outfit.user_id == user_id).first()
    if not outfit:
        raise HTTPException(status_code=404, detail="Outfit not found")

    if outfit_update.image_url is not None:
        if outfit.image_url and outfit.image_url != outfit_update.image_url:
            delete_local_file(outfit.image_url)
        outfit.image_url = outfit_update.image_url

    # 2. 更新基础字段
    if outfit_update.name is not None: outfit.name = outfit_update.name
    if outfit_update.description is not None: outfit.description = outfit_update.description
    if outfit_update.season is not None: outfit.season = outfit_update.season
    if outfit_update.style is not None: outfit.style = outfit_update.style
    if outfit_update.meta_data is not None: outfit.meta_data = outfit_update.meta_data

    # 3. 更新关联 Items (先删后加策略，最简单)
    if outfit_update.items is not None:
        # 删除旧引用
        db.query(models.OutfitRef).filter(models.OutfitRef.outfit_id == outfit_id).delete()
        
        # 添加新引用
        new_refs = []
        for item_data in outfit_update.items:
            ref = models.OutfitRef(
                outfit_id=outfit_id,
                item_id=item_data.item_id,
                position_x=item_data.position_x,
                position_y=item_data.position_y,
                rotation=item_data.rotation,
                scale_x=item_data.scale_x,
                scale_y=item_data.scale_y,
                z_index=item_data.z_index,
            )
            new_refs.append(ref)
        db.add_all(new_refs)

    db.commit()
    db.refresh(outfit)
    return {"message": "Updated successfully", "outfit_id": outfit.outfit_id}

# ==========================================
# 3. 获取用户所有搭配列表
# ==========================================
@router.get("/", response_model=List[schemas.OutfitOut])
def list_outfits(
    db: Session = Depends(get_db),
    user_id: int = Depends(security.get_current_user_id)
):
    outfits_with_count = (
        db.query(
            models.Outfit, 
            func.count(models.OutfitRef.item_id).label("item_count")
        )
        .filter(models.Outfit.user_id == user_id)
        .outerjoin(models.OutfitRef)
        .group_by(models.Outfit.outfit_id)
        .order_by(models.Outfit.create_time.desc())
        .all()
    )
    
    outfit_list = []
    for outfit, item_count in outfits_with_count:
        outfit_data = schemas.OutfitOut(
            outfit_id=outfit.outfit_id,
            name=outfit.name,
            season=outfit.season,
            style=outfit.style,
            image_url=outfit.image_url,
            create_time=outfit.create_time,
            item_count=item_count
        )
        outfit_list.append(outfit_data)
        
    return outfit_list

# ==========================================
# 4. 获取搭配详情
# ==========================================
@router.get("/{outfit_id}", response_model=schemas.OutfitDetailOut)
def get_outfit_detail(
    outfit_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(security.get_current_user_id)
):
    outfit = (
        db.query(models.Outfit)
        .filter(models.Outfit.outfit_id == outfit_id, models.Outfit.user_id == user_id)
        .first()
    )
    
    if not outfit:
        raise HTTPException(status_code=404, detail="找不到该搭配")

    # [修改] 使用 ClothingItem
    outfit_items_query = (
        db.query(models.ClothingItem, models.OutfitRef)
        .join(models.OutfitRef, models.OutfitRef.item_id == models.ClothingItem.item_id)
        .filter(models.OutfitRef.outfit_id == outfit_id)
        .order_by(models.OutfitRef.z_index.asc()) 
        .all()
    )
    
    items_list = []
    for item, ref in outfit_items_query:
        # [修改] 安全地获取分类名称
        cat_name = item.category.category_name if item.category else "Uncategorized"
        
        item_detail = schemas.OutfitItemDetailOut(
            item_id=item.item_id,
            name=item.name,
            category=cat_name, 
            image_url=item.image_url,
            position_x=ref.position_x,
            position_y=ref.position_y,
            rotation=ref.rotation,
            scale_x=ref.scale_x,
            scale_y=ref.scale_y,
            z_index=ref.z_index,
        )
        items_list.append(item_detail)

    return schemas.OutfitDetailOut(
        outfit_id=outfit.outfit_id,
        name=outfit.name,
        description=outfit.description,
        season=outfit.season,
        style=outfit.style,
        image_url=outfit.image_url,
        create_time=outfit.create_time,
        meta_data=outfit.meta_data,
        items=items_list
    )

@router.delete("/{outfit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_outfit(
    outfit_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(security.get_current_user_id)
):
    outfit = db.query(models.Outfit).filter(models.Outfit.outfit_id == outfit_id, models.Outfit.user_id == user_id).first()
    if not outfit:
        raise HTTPException(status_code=404, detail="Not Found")
    if outfit.image_url:
        delete_local_file(outfit.image_url)
    db.delete(outfit)
    db.commit()
    return

@router.get("/assets/{asset_type}")
def get_assets(asset_type: str):
    """
    asset_type 可以是 'textures' 或 'decor'
    """
    base_url = "http://localhost:8000/static"
    folder_path = os.path.join("static", asset_type)
    
    if not os.path.exists(folder_path):
        return []
        
    files = os.listdir(folder_path)
    # 过滤图片文件
    images = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    # 返回完整的 URL 列表
    return [
        {
            "name": img,
            "src": f"{base_url}/{asset_type}/{img}"
        }
        for img in images
    ]
