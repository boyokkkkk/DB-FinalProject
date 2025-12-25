from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import List, Optional
from database import get_db
import models, schemas
import security
import re

router = APIRouter(
    prefix="/api/closet",
    tags=["closet"]
)

# ========== 新增：中文搜索辅助函数 ==========
def build_chinese_search_filter(field, keyword):
    """
    构建中文模糊搜索过滤条件（兼容中英文，优化匹配效率）
    :param field: 数据库字段
    :param keyword: 搜索关键词
    :return: sqlalchemy 过滤条件
    """
    # 去除关键词空格，支持中文分词片段匹配
    keyword = re.sub(r'\s+', '', keyword).strip()
    if not keyword:
        return None
    # 优化：用 concat 减少 % 前缀（若有索引可走索引扫描），中文用 like 兼容
    return field.like(f"%{keyword}%")

@router.get("/categories", response_model=List[schemas.Category])
def get_categories(
    db: Session = Depends(get_db),
    user_id: int = Depends(security.get_current_user_id) # 需登录
):
    """获取所有分类，Item数量只统计当前用户的"""
    categories = db.query(models.Category).all()
    result = []
    for category in categories:
        # 增加 user_id 过滤
        count = db.query(func.count(models.ClothingItem.item_id))\
                 .filter(
                     models.ClothingItem.category_id == category.category_id,
                     models.ClothingItem.user_id == user_id 
                 ).scalar()
        category_dict = category.__dict__
        category_dict['item_count'] = count
        result.append(category_dict)
    return result

@router.get("/category/{category_id}", response_model=schemas.CategoryWithClothes)
def get_category_with_clothes(
    category_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db),
    user_id: int = Depends(security.get_current_user_id) # [新增]
):
    """获取分类下的衣物 (仅限当前用户)"""
    category = db.query(models.Category).filter(models.Category.category_id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # [修改] 增加 user_id 过滤
    clothes = db.query(models.ClothingItem)\
                .filter(
                    models.ClothingItem.category_id == category_id,
                    models.ClothingItem.user_id == user_id
                )\
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
    db: Session = Depends(get_db),
    user_id: int = Depends(security.get_current_user_id) # [新增]
):
    """搜索衣物 (仅限当前用户)"""
    try:
        query_obj = db.query(models.ClothingItem).filter(models.ClothingItem.user_id == user_id)

        filters = []

        if query and query.strip():
            search_conditions = []
            # 名称（核心字段）
            name_filter = build_chinese_search_filter(models.ClothingItem.name, query)
            if name_filter:
                search_conditions.append(name_filter)
            # 品牌
            brand_filter = build_chinese_search_filter(models.ClothingItem.brand, query)
            if brand_filter:
                search_conditions.append(brand_filter)
            # 颜色
            color_filter = build_chinese_search_filter(models.ClothingItem.color, query)
            if color_filter:
                search_conditions.append(color_filter)
            # 季节
            season_filter = build_chinese_search_filter(models.ClothingItem.season, query)
            if season_filter:
                search_conditions.append(season_filter)
            # 风格
            style_filter = build_chinese_search_filter(models.ClothingItem.style, query)
            if style_filter:
                search_conditions.append(style_filter)
            # 场景
            occasion_filter = build_chinese_search_filter(models.ClothingItem.occasion, query)
            if occasion_filter:
                search_conditions.append(occasion_filter)

            if search_conditions:
                filters.append(or_(*search_conditions))

            # 2.2 分类过滤（精准匹配）
        if category_id:
            filters.append(models.ClothingItem.category_id == category_id)

            # 2.3 颜色过滤（中文支持，如：黑色、白色）
        if color and color.strip():
            color_filter = build_chinese_search_filter(models.ClothingItem.color, color)
            if color_filter:
                filters.append(color_filter)

            # 2.4 季节过滤（中文支持，如：春季、冬季）
        if season and season.strip():
            season_filter = build_chinese_search_filter(models.ClothingItem.season, season)
            if season_filter:
                filters.append(season_filter)

            # 3. 应用所有过滤条件（优化：避免空filter导致全表扫描）
        if filters:
            query_obj = query_obj.filter(*filters)

            # 4. 性能优化：
            # - distinct() 去重（按需保留，若无重复可删除）
            # - 先分页再查询，减少数据加载
        items = query_obj.distinct().offset(skip).limit(limit).all()

        return items

    except Exception as e:
        # 异常时手动回滚 + 精准报错
        db.rollback()
        error_detail = f"搜索失败：{str(e)}，关键词：{query}，用户ID：{user_id}"
        print(error_detail)
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")

@router.get("/items/{item_id}", response_model=schemas.ClothingItem)
def get_item(
    item_id: int, 
    db: Session = Depends(get_db),
    user_id: int = Depends(security.get_current_user_id) # [新增]
):
    """获取衣物详情 (需验证归属权)"""
    item = db.query(models.ClothingItem)\
             .filter(
                 models.ClothingItem.item_id == item_id,
                 models.ClothingItem.user_id == user_id # 只能查自己的
             ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.post("/items", response_model=schemas.ClothingItem)
def create_item(
    item: schemas.ClothingItemCreate, 
    db: Session = Depends(get_db),
    user_id: int = Depends(security.get_current_user_id) # [新增]
):
    """创建衣物"""
    try:
        # 忽略前端传来的 user_id，强制使用 Token 中的 user_id
        item_data = item.dict()
        item_data['user_id'] = user_id
        print(user_id)
        
        tag_ids = item_data.pop('tag_ids', [])

        # 检查分类是否存在
        category = db.query(models.Category).filter(models.Category.category_id == item_data['category_id']).first()
        if not category:
            raise HTTPException(status_code=404, detail=f"分类ID {item_data['category_id']} 不存在")

        db_item = models.ClothingItem(**item_data)
        db.add(db_item)
        db.flush()

        # 添加标签
        if tag_ids:
            for tag_id in tag_ids:
                tag = db.query(models.Tag).filter(models.Tag.tag_id == tag_id).first()
                if tag:
                    db.execute(
                        models.clothing_tags.insert().values(
                            item_id=db_item.item_id,
                            tag_id=tag_id
                        )
                    )

        db.commit()
        db.refresh(db_item)
        return db_item
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"创建衣物失败: {str(e)}")

@router.put("/items/{item_id}", response_model=schemas.ClothingItem)
def update_item(
    item_id: int, 
    item_update: schemas.ClothingItemCreate, 
    db: Session = Depends(get_db),
    user_id: int = Depends(security.get_current_user_id)
):
    """更新衣物"""
    db_item = db.query(models.ClothingItem)\
                .filter(models.ClothingItem.item_id == item_id, models.ClothingItem.user_id == user_id)\
                .first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")

    try:
        # 不允许修改 user_id
        update_data = item_update.dict(exclude={'tag_ids', 'user_id'})
        for key, value in update_data.items():
            setattr(db_item, key, value)

        if item_update.tag_ids is not None:
            db.execute(models.clothing_tags.delete().where(models.clothing_tags.c.item_id == item_id))
            for tag_id in item_update.tag_ids:
                db.execute(models.clothing_tags.insert().values(item_id=item_id, tag_id=tag_id))

        db.commit()
        db.refresh(db_item)
        return db_item
    except Exception as e:
        # 修复：捕获异常并打印，避免静默回滚
        db.rollback()
        print(f"更新失败：{str(e)}")
        raise HTTPException(status_code=500, detail=f"Update failed: {str(e)}")

@router.delete("/items/{item_id}")
def delete_item(
    item_id: int, 
    db: Session = Depends(get_db),
    user_id: int = Depends(security.get_current_user_id)
):
    """删除衣物"""
    db_item = db.query(models.ClothingItem)\
                .filter(models.ClothingItem.item_id == item_id, models.ClothingItem.user_id == user_id)\
                .first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    db.delete(db_item)
    db.commit()
    return {"message": "Item deleted successfully"}