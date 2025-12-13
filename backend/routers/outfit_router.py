from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

# 导入自定义模块
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
@router.get("/items", response_model=List[schemas.ItemOut])
def get_user_items(
    db: Session = Depends(get_db),
    user_id: int = Depends(security.get_current_user_id)
):
    """
    获取当前用户衣橱中所有的单品列表。
    """
    items = db.query(models.Item).filter(models.Item.user_id == user_id).all()
    return items

# ==========================================
# 2. 创建/保存一个搭配 (OutfitStudio 保存按钮)
# ==========================================
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_outfit(
    outfit_data: schemas.OutfitCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(security.get_current_user_id)
):
    """
    保存一个新的搭配方案。
    """
    if not outfit_data.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="搭配必须包含至少一件单品"
        )
    
    # 1. 创建 Outfit 主记录
    new_outfit = models.Outfit(
        user_id=user_id,
        name=outfit_data.name,
        description=outfit_data.description,
        season=outfit_data.season,
        style=outfit_data.style,
        image_url=outfit_data.image_url,
    )
    db.add(new_outfit)
    db.commit()
    db.refresh(new_outfit)
    
    # 2. 创建 OutfitRef 关联记录
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

# ==========================================
# 3. 获取用户所有搭配列表 (OutfitBoard 页面)
# ==========================================
@router.get("/", response_model=List[schemas.OutfitOut])
def list_outfits(
    db: Session = Depends(get_db),
    user_id: int = Depends(security.get_current_user_id)
):
    """
    获取当前用户所有的搭配列表（仅包含概要信息）。
    """
    # 使用 join/group_by 统计每套搭配包含的单品数量
    outfits_with_count = (
        db.query(
            models.Outfit, 
            func.count(models.OutfitRef.item_id).label("item_count")
        )
        .filter(models.Outfit.user_id == user_id)
        .outerjoin(models.OutfitRef) # 使用 OuterJoin 保证没有单品的搭配也能显示 (item_count=0)
        .group_by(models.Outfit.outfit_id)
        .order_by(models.Outfit.create_time.desc())
        .all()
    )
    
    # 格式化输出
    outfit_list = []
    for outfit, item_count in outfits_with_count:
        outfit_data = schemas.OutfitOut(
            outfit_id=outfit.outfit_id,
            name=outfit.name,
            season=outfit.season,
            style=outfit.style,
            image_url=outfit.image_url,
            create_time=outfit.create_time,
            item_count=item_count  # <--- 这里传入我们计算好的数量
        )
        outfit_list.append(outfit_data)
        
    return outfit_list

# ==========================================
# 4. 获取搭配详情 (OutfitStudio 加载搭配)
# ==========================================
@router.get("/{outfit_id}", response_model=schemas.OutfitDetailOut)
def get_outfit_detail(
    outfit_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(security.get_current_user_id)
):
    """
    根据 ID 获取搭配的详细信息，包括所有单品及其在画布上的位置信息。
    """
    outfit = (
        db.query(models.Outfit)
        .filter(models.Outfit.outfit_id == outfit_id, models.Outfit.user_id == user_id)
        .first()
    )
    
    if not outfit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="找不到该搭配或无权限访问"
        )

    # 查询关联的单品和位置信息
    outfit_items_query = (
        db.query(models.Item, models.OutfitRef)
        .join(models.OutfitRef, models.OutfitRef.item_id == models.Item.item_id)
        .filter(models.OutfitRef.outfit_id == outfit_id)
        .order_by(models.OutfitRef.z_index.desc()) # 按图层顺序返回
        .all()
    )
    
    items_list = []
    for item, ref in outfit_items_query:
        item_detail = schemas.OutfitItemDetailOut(
            item_id=item.item_id,
            name=item.name,
            category=item.category,
            image_url=item.image_url,
            # 画布位置信息
            position_x=ref.position_x,
            position_y=ref.position_y,
            rotation=ref.rotation,
            scale_x=ref.scale_x,
            scale_y=ref.scale_y,
            z_index=ref.z_index,
        )
        items_list.append(item_detail)

    # 4. [修改核心] 手动构造最终响应对象
    return schemas.OutfitDetailOut(
        outfit_id=outfit.outfit_id,
        name=outfit.name,
        description=outfit.description,
        season=outfit.season,
        style=outfit.style,
        image_url=outfit.image_url,
        create_time=outfit.create_time,
        items=items_list  # 把构造好的列表塞进去
    )

# ==========================================
# 5. 删除搭配
# ==========================================
@router.delete("/{outfit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_outfit(
    outfit_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(security.get_current_user_id)
):
    """
    删除指定的搭配方案。由于设置了 ON DELETE CASCADE，关联表记录也会自动删除。
    """
    outfit = (
        db.query(models.Outfit)
        .filter(models.Outfit.outfit_id == outfit_id, models.Outfit.user_id == user_id)
        .first()
    )
    
    if not outfit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="找不到该搭配或无权限访问"
        )
        
    db.delete(outfit)
    db.commit()
    return

# ==========================================
# 6. 更新搭配（可作为练习，基本与创建类似，需要先删除旧的 ref 再添加新的）
# ==========================================
# 暂不实现，以上 CRUD 已满足基本项目要求。