from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, func, text
from typing import List, Optional
from datetime import datetime
import models, schemas
from database import get_db
import security
from difflib import SequenceMatcher

router = APIRouter(
    prefix="/api/wishlist",
    tags=["wishlist"]
)


@router.get("/items", response_model=List[schemas.WishlistItemWithTags])
def get_wishlist_items(
        skip: int = Query(0, ge=0),
        limit: int = Query(20, le=100),
        added_to_closet: Optional[bool] = Query(None),
        db: Session = Depends(get_db),
        user_id: int = Depends(security.get_current_user_id)
):
    """获取用户的心愿单列表"""
    try:
        query = db.query(models.WishlistItem) \
            .options(joinedload(models.WishlistItem.tags)) \
            .filter(models.WishlistItem.user_id == user_id)

        if added_to_closet is not None:
            query = query.filter(models.WishlistItem.added_to_closet == added_to_closet)

        items = query.order_by(models.WishlistItem.created_at.desc()) \
            .offset(skip) \
            .limit(limit) \
            .all()

        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取心愿单失败: {str(e)}")


@router.get("/items/{wishlist_id}", response_model=schemas.WishlistItemWithTags)
def get_wishlist_item(
        wishlist_id: int,
        db: Session = Depends(get_db),
        user_id: int = Depends(security.get_current_user_id)
):
    """获取心愿单项目详情"""
    item = db.query(models.WishlistItem) \
        .options(joinedload(models.WishlistItem.tags)) \
        .filter(
        models.WishlistItem.wishlist_id == wishlist_id,
        models.WishlistItem.user_id == user_id
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Wishlist item not found")

    return item


@router.post("/items", response_model=schemas.WishlistItemWithTags)
def create_wishlist_item(
        item: schemas.WishlistItemCreate,
        db: Session = Depends(get_db),
        user_id: int = Depends(security.get_current_user_id)
):
    """创建心愿单项目"""
    try:
        item_data = item.dict()
        item_data['user_id'] = user_id
        tag_ids = item_data.pop('tag_ids', [])

        # 检查分类是否存在
        if item_data.get('category_id'):
            category = db.query(models.Category) \
                .filter(models.Category.category_id == item_data['category_id']) \
                .first()
            if not category:
                raise HTTPException(status_code=404, detail="Category not found")

        # 创建心愿单项目
        db_item = models.WishlistItem(**item_data)
        db.add(db_item)
        db.flush()

        # 添加标签
        if tag_ids:
            for tag_id in tag_ids:
                tag = db.query(models.Tag).filter(models.Tag.tag_id == tag_id).first()
                if tag:
                    db.execute(
                        models.wishlist_tags.insert().values(
                            wishlist_id=db_item.wishlist_id,
                            tag_id=tag_id
                        )
                    )

        db.commit()
        db.refresh(db_item)
        return db_item

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"创建心愿单项目失败: {str(e)}")


@router.put("/items/{wishlist_id}", response_model=schemas.WishlistItemWithTags)
def update_wishlist_item(
        wishlist_id: int,
        item_update: schemas.WishlistItemUpdate,
        db: Session = Depends(get_db),
        user_id: int = Depends(security.get_current_user_id)
):
    """更新心愿单项目"""
    try:
        db_item = db.query(models.WishlistItem) \
            .filter(
            models.WishlistItem.wishlist_id == wishlist_id,
            models.WishlistItem.user_id == user_id
        ).first()

        if not db_item:
            raise HTTPException(status_code=404, detail="Wishlist item not found")

        # 更新基本字段
        update_data = item_update.dict(exclude_unset=True, exclude={'tag_ids'})
        for key, value in update_data.items():
            setattr(db_item, key, value)

        # 更新标签
        if 'tag_ids' in item_update.dict(exclude_unset=True):
            db.execute(models.wishlist_tags.delete().where(
                models.wishlist_tags.c.wishlist_id == wishlist_id
            ))

            if item_update.tag_ids:
                for tag_id in item_update.tag_ids:
                    tag = db.query(models.Tag).filter(models.Tag.tag_id == tag_id).first()
                    if tag:
                        db.execute(
                            models.wishlist_tags.insert().values(
                                wishlist_id=wishlist_id,
                                tag_id=tag_id
                            )
                        )

        db.commit()
        db.refresh(db_item)
        return db_item

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"更新心愿单项目失败: {str(e)}")


@router.delete("/items/{wishlist_id}")
def delete_wishlist_item(
        wishlist_id: int,
        db: Session = Depends(get_db),
        user_id: int = Depends(security.get_current_user_id)
):
    """删除心愿单项目"""
    db_item = db.query(models.WishlistItem) \
        .filter(
        models.WishlistItem.wishlist_id == wishlist_id,
        models.WishlistItem.user_id == user_id
    ).first()

    if not db_item:
        raise HTTPException(status_code=404, detail="Wishlist item not found")

    db.delete(db_item)
    db.commit()
    return {"message": "Wishlist item deleted successfully"}


@router.post("/items/{wishlist_id}/add-to-closet", response_model=schemas.ClothingItem)
def add_to_closet(
        wishlist_id: int,
        db: Session = Depends(get_db),
        user_id: int = Depends(security.get_current_user_id)
):
    """将心愿单项目添加到衣橱"""
    try:
        # 获取心愿单项目
        wishlist_item = db.query(models.WishlistItem) \
            .filter(
            models.WishlistItem.wishlist_id == wishlist_id,
            models.WishlistItem.user_id == user_id
        ).first()

        if not wishlist_item:
            raise HTTPException(status_code=404, detail="Wishlist item not found")

        if wishlist_item.added_to_closet:
            raise HTTPException(status_code=400, detail="Item already added to closet")

        # 获取标签
        tag_ids = db.query(models.wishlist_tags.c.tag_id) \
            .filter(models.wishlist_tags.c.wishlist_id == wishlist_id) \
            .all()
        tag_ids = [tag_id[0] for tag_id in tag_ids]

        # 创建衣橱项目
        closet_item_data = {
            'user_id': user_id,
            'name': wishlist_item.name,
            'brand': wishlist_item.brand,
            'color': wishlist_item.color,
            'season': wishlist_item.season,
            'occasion': wishlist_item.occasion,
            'style': wishlist_item.style,
            'material': wishlist_item.material,
            'category_id': wishlist_item.category_id,
            'price': wishlist_item.price,
            'image_url': wishlist_item.image_url,
            'notes': wishlist_item.notes
        }

        # 检查必填字段
        if not closet_item_data.get('category_id'):
            raise HTTPException(status_code=400, detail="Category is required to add to closet")

        # 创建衣橱项目
        closet_item = models.ClothingItem(**closet_item_data)
        db.add(closet_item)
        db.flush()

        # 添加标签
        if tag_ids:
            for tag_id in tag_ids:
                db.execute(
                    models.clothing_tags.insert().values(
                        item_id=closet_item.item_id,
                        tag_id=tag_id
                    )
                )

        # 更新心愿单项目状态
        wishlist_item.added_to_closet = True
        wishlist_item.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(closet_item)
        return closet_item

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"添加到衣橱失败: {str(e)}")


@router.get("/items/{wishlist_id}/similar-items", response_model=List[schemas.SimilarClothingItem])
def find_similar_items(
        wishlist_id: int,
        threshold: float = Query(0.01, ge=0, le=1, description="相似度阈值，0-1之间"),
        limit: int = Query(10, ge=1, le=50, description="返回结果数量限制"),
        db: Session = Depends(get_db),
        user_id: int = Depends(security.get_current_user_id)
):
    """查找衣橱中类似的项目"""
    try:
        # 获取心愿单项目
        wishlist_item = db.query(models.WishlistItem) \
            .filter(
                models.WishlistItem.wishlist_id == wishlist_id,
                models.WishlistItem.user_id == user_id
        ).first()

        if not wishlist_item:
            raise HTTPException(status_code=404, detail="Wishlist item not found")

        # 获取用户的所有衣橱项目
        closet_items = db.query(models.ClothingItem) \
            .filter(models.ClothingItem.user_id == user_id) \
            .all()

        similar_items = []
        print(f"要求为：{threshold}")

        for closet_item in closet_items:
            # 计算综合相似度
            total_similarity, field_similarities = calculate_similarity(
                wishlist_item,
                closet_item
            )
            print(f"相似度为：{total_similarity}")

            if total_similarity >= threshold:
                # 收集匹配的字段
                match_fields = []
                high_similarity_fields = []

                for field, similarity in field_similarities.items():
                    if similarity > 0.7:  # 高相似度字段
                        high_similarity_fields.append(field)
                    elif similarity > 0.4:  # 一般匹配字段
                        match_fields.append(field)

                # 优先显示高相似度字段
                display_fields = high_similarity_fields if high_similarity_fields else match_fields

                similar_items.append({
                    "item_id": closet_item.item_id,
                    "name": closet_item.name,
                    "brand": closet_item.brand,
                    "color": closet_item.color,
                    "season": closet_item.season,
                    "occasion": closet_item.occasion,
                    "style": closet_item.style,
                    "category": closet_item.category.category_name if closet_item.category else None,
                    "image_url": closet_item.image_url,
                    "price": closet_item.price,
                    "similarity_score": round(total_similarity, 3),
                    "match_fields": display_fields,
                    "match_details": {  # 添加详细匹配信息
                        "name_similarity": field_similarities['name'],
                        "brand_similarity": field_similarities['brand'],
                        "color_similarity": field_similarities['color'],
                        "category_match": field_similarities['category'] > 0,
                        "season_similarity": field_similarities['season']
                    }
                })

        # 按相似度排序并限制数量
        similar_items.sort(key=lambda x: x["similarity_score"], reverse=True)

        # 返回前N个结果
        return similar_items[:limit]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查找相似项目失败: {str(e)}")

def calculate_similarity(wishlist_item, closet_item, weights=None):
    """计算两个项目之间的相似度"""
    if weights is None:
        weights = {
            'name': 0.2,  # 名称相似度权重
            'brand': 0.05,  # 品牌相似度权重
            'color': 0.3,  # 颜色相似度权重
            'category': 0.25,  # 分类权重
            'season': 0.1,  # 季节权重
            'occasion': 0.05,  # 场合权重
            'style': 0.05  # 风格权重
        }

    similarities = {}

    # 1. 名称相似度（使用模糊匹配）
    similarities['name'] = calculate_text_similarity(
        wishlist_item.name,
        closet_item.name
    )

    # 2. 品牌相似度
    similarities['brand'] = calculate_text_similarity(
        wishlist_item.brand or '',
        closet_item.brand or ''
    )

    # 3. 颜色相似度（特殊处理）
    similarities['color'] = calculate_color_similarity(
        wishlist_item.color,
        closet_item.color
    )

    # 4. 分类相似度（精确匹配）
    similarities['category'] = 1.0 if (
            wishlist_item.category_id and
            wishlist_item.category_id == closet_item.category_id
    ) else 0.0

    # 5. 季节相似度
    similarities['season'] = calculate_season_similarity(
        wishlist_item.season,
        closet_item.season
    )

    # 6. 场合相似度
    similarities['occasion'] = calculate_text_similarity(
        wishlist_item.occasion or '',
        closet_item.occasion or ''
    )

    # 7. 风格相似度
    similarities['style'] = calculate_text_similarity(
        wishlist_item.style or '',
        closet_item.style or ''
    )

    # 计算加权相似度
    total_similarity = 0
    for field, weight in weights.items():
        total_similarity += similarities[field] * weight

    return total_similarity, similarities


def calculate_text_similarity(text1, text2):
    """计算两个文本的相似度，支持模糊匹配"""
    if not text1 or not text2:
        return 0.0

    # 转换为小写去除大小写影响
    text1 = text1.lower().strip()
    text2 = text2.lower().strip()

    # 完全匹配
    if text1 == text2:
        return 1.0

    # 包含关系
    if text1 in text2 or text2 in text1:
        return 0.8

    # 使用序列匹配计算相似度
    similarity = SequenceMatcher(None, text1, text2).ratio()

    # 如果相似度超过阈值，认为是相似的
    if similarity > 0.1:
        return similarity

    return 0.0


def calculate_color_similarity(color1, color2):
    """计算颜色相似度"""
    if not color1 or not color2:
        return 0.0

    color1 = color1.lower().strip()
    color2 = color2.lower().strip()

    # 完全匹配
    if color1 == color2:
        return 1.0

    # 颜色映射表，将相似颜色分组
    color_groups = {
        'red': ['red', 'crimson', 'scarlet', 'ruby', 'cherry', 'burgundy'],
        'blue': ['blue', 'navy', 'sky', 'azure', 'cobalt', 'teal'],
        'green': ['green', 'emerald', 'olive', 'lime', 'mint', 'forest'],
        'black': ['black', 'charcoal', 'onyx', 'ebony'],
        'white': ['white', 'ivory', 'cream', 'beige', 'off-white'],
        'gray': ['gray', 'grey', 'slate', 'silver', 'ash'],
        'brown': ['brown', 'tan', 'beige', 'chocolate', 'coffee', 'caramel'],
        'purple': ['purple', 'violet', 'lavender', 'lilac', 'mauve'],
        'pink': ['pink', 'rose', 'salmon', 'coral', 'fuchsia'],
        'yellow': ['yellow', 'gold', 'amber', 'mustard', 'lemon'],
        'orange': ['orange', 'peach', 'coral', 'apricot', 'tangerine']
    }

    # 检查是否属于同一颜色组
    for group, colors in color_groups.items():
        if color1 in colors and color2 in colors:
            return 0.7  # 同一颜色组

    # 检查颜色名称是否包含关系
    if color1 in color2 or color2 in color1:
        return 0.5

    return 0.0


def calculate_season_similarity(season1, season2):
    """计算季节相似度"""
    if not season1 or not season2:
        return 0.0

    # 完全匹配
    if season1 == season2:
        return 1.0

    # All Seasons 与其他任何季节都匹配
    if season1 == 'All Seasons' or season2 == 'All Seasons':
        return 0.7

    # 季节相似度矩阵
    season_similarity = {
        'Spring': {'Summer': 0.6, 'Autumn': 0.4, 'Winter': 0.2},
        'Summer': {'Spring': 0.6, 'Autumn': 0.4, 'Winter': 0.2},
        'Autumn': {'Spring': 0.4, 'Summer': 0.4, 'Winter': 0.6},
        'Winter': {'Spring': 0.2, 'Summer': 0.2, 'Autumn': 0.6}
    }

    if season1 in season_similarity and season2 in season_similarity[season1]:
        return season_similarity[season1][season2]

    return 0.0




@router.get("/stats")
def get_wishlist_stats(
        db: Session = Depends(get_db),
        user_id: int = Depends(security.get_current_user_id)
):
    """获取心愿单统计信息"""
    try:
        total_items = db.query(func.count(models.WishlistItem.wishlist_id)) \
            .filter(models.WishlistItem.user_id == user_id) \
            .scalar()

        added_to_closet = db.query(func.count(models.WishlistItem.wishlist_id)) \
            .filter(
            models.WishlistItem.user_id == user_id,
            models.WishlistItem.added_to_closet == True
        ) \
            .scalar()

        by_category = db.query(
            models.Category.category_name,
            func.count(models.WishlistItem.wishlist_id)
        ) \
            .join(models.WishlistItem, models.WishlistItem.category_id == models.Category.category_id) \
            .filter(models.WishlistItem.user_id == user_id) \
            .group_by(models.Category.category_name) \
            .all()

        return {
            "total_items": total_items or 0,
            "added_to_closet": added_to_closet or 0,
            "not_added": (total_items or 0) - (added_to_closet or 0),
            "by_category": dict(by_category) if by_category else {}
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")