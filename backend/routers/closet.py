from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import List, Optional
import sys
from database import get_db
import models, schemas

router = APIRouter(
    prefix="/api/closet",
    tags=["closet"]
)

@router.get("/categories", response_model=List[schemas.Category])
def get_categories(db: Session = Depends(get_db)):
    """获取所有分类及衣物数量"""
    categories = db.query(models.Category).all()
    result = []
    for category in categories:
        count = db.query(func.count(models.ClothingItem.item_id))\
                 .filter(models.ClothingItem.category_id == category.category_id)\
                 .scalar()
        category_dict = category.__dict__
        category_dict['item_count'] = count
        result.append(category_dict)
    return result

@router.get("/category/{category_id}", response_model=schemas.CategoryWithClothes)
def get_category_with_clothes(
    category_id: int,
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, le=100)
):
    """获取分类下的衣物"""
    category = db.query(models.Category)\
                 .filter(models.Category.category_id == category_id)\
                 .first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    clothes = db.query(models.ClothingItem)\
                .filter(models.ClothingItem.category_id == category_id)\
                .offset(skip)\
                .limit(limit)\
                .all()
    
    result = category.__dict__
    result['clothes'] = clothes
    return result

@router.get("/items/search", response_model=List[schemas.ClothingItem])
def search_items(
    query: Optional[str] = Query(None),
    category_id: Optional[int] = Query(None),
    color: Optional[str] = Query(None),
    season: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db)
):
    """搜索衣物"""
    filters = []
    if query:
        filters.append(
            or_(
                models.ClothingItem.name.ilike(f"%{query}%"),
                models.ClothingItem.brand.ilike(f"%{query}%"),
                models.ClothingItem.color.ilike(f"%{query}%")
            )
        )
    if category_id:
        filters.append(models.ClothingItem.category_id == category_id)
    if color:
        filters.append(models.ClothingItem.color.ilike(f"%{color}%"))
    if season:
        filters.append(models.ClothingItem.season.ilike(f"%{season}%"))
    
    items = db.query(models.ClothingItem)\
              .filter(*filters)\
              .offset(skip)\
              .limit(limit)\
              .all()
    return items

@router.get("/items/{item_id}", response_model=schemas.ClothingItem)
def get_item(item_id: int, db: Session = Depends(get_db)):
    """获取衣物详情"""
    item = db.query(models.ClothingItem)\
             .filter(models.ClothingItem.item_id == item_id)\
             .first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.post("/items", response_model=schemas.ClothingItem)
def create_item(item: schemas.ClothingItemCreate, db: Session = Depends(get_db)):
    """创建衣物"""
    try:
        # 先验证 item 数据
        print(f"📥 接收到的数据: {item.dict()}")

        # 检查必要字段
        if not item.user_id:
            raise HTTPException(status_code=400, detail="user_id 是必填字段")

        if not item.category_id:
            raise HTTPException(status_code=400, detail="category_id 是必填字段")

        # 检查用户是否存在
        user = db.query(models.User).filter(models.User.user_id == item.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail=f"用户ID {item.user_id} 不存在")

        # 检查分类是否存在
        category = db.query(models.Category).filter(models.Category.category_id == item.category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail=f"分类ID {item.category_id} 不存在")

        # 准备数据
        item_data = item.dict()
        tag_ids = item_data.pop('tag_ids', [])

        print(f"📝 准备插入的数据: {item_data}")

        # 创建衣物对象
        db_item = models.ClothingItem(**item_data)
        db.add(db_item)
        db.flush()  # 先flush获取item_id

        print(f"✅ 衣物创建成功，item_id: {db_item.item_id}")
    
        # 添加标签
        if tag_ids:
            print(f"🏷️ 准备添加标签: {tag_ids}")
            for tag_id in tag_ids:
                tag = db.query(models.Tag).filter(models.Tag.tag_id == tag_id).first()
                if tag:
                    db.execute(
                        models.clothing_tags.insert().values(
                            item_id=db_item.item_id,
                            tag_id=tag_id
                        )
                    )
                    print(f"  关联标签 {tag_id}")

        db.commit()
        db.refresh(db_item)
        print(f"🎉 衣物保存完成: {db_item.item_id}")
    
        return db_item
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 创建衣物失败: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"创建衣物失败: {str(e)}")

@router.put("/items/{item_id}", response_model=schemas.ClothingItem)
def update_item(item_id: int, item_update: schemas.ClothingItemCreate, db: Session = Depends(get_db)):
    """更新衣物"""
    db_item = db.query(models.ClothingItem)\
                .filter(models.ClothingItem.item_id == item_id)\
                .first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    for key, value in item_update.dict(exclude={'tag_ids'}).items():
        setattr(db_item, key, value)
    
    # 更新标签
    if item_update.tag_ids is not None:
        # 删除现有标签
        db.execute(
            models.clothing_tags.delete().where(
                models.clothing_tags.c.item_id == item_id
            )
        )
        # 添加新标签
        for tag_id in item_update.tag_ids:
            db.execute(
                models.clothing_tags.insert().values(
                    item_id=item_id,
                    tag_id=tag_id
                )
            )
    
    db.commit()
    db.refresh(db_item)
    return db_item

@router.delete("/items/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    """删除衣物"""
    db_item = db.query(models.ClothingItem)\
                .filter(models.ClothingItem.item_id == item_id)\
                .first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    db.delete(db_item)
    db.commit()
    return {"message": "Item deleted successfully"}