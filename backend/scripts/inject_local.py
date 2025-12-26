import sys
import os
import json
from datetime import datetime

# 1. 路径设置
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from database import SessionLocal
import models

# 直接指向最终存放图片的目录
TARGET_DIR = os.path.join(BASE_DIR, "static", "uploads", "items")
# JSON 文件也放在这里
DATA_FILE = os.path.join(TARGET_DIR, "items.json")

def load_items_from_json():
    """从 JSON 文件加载数据"""
    if not os.path.exists(DATA_FILE):
        print(f"❌ 错误: 在 {TARGET_DIR} 下找不到 items.json")
        print("请确保你已经把 items.json 和图片都放到了 static/uploads/items/ 目录下。")
        return []
    
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ 读取 JSON 失败: {e}")
        return []

def inject_data():
    print(f"=== 开始注入数据库 (原地模式) ===")
    print(f"数据目录: {TARGET_DIR}")
    
    # 1. 加载数据
    local_items = load_items_from_json()
    if not local_items:
        return

    print(f"找到 {len(local_items)} 条数据，准备入库...")

    db = SessionLocal()
    try:
        target_user_id = 1
        
        user = db.query(models.User).filter(models.User.user_id == target_user_id).first()

        if not user:
            print(f"⚠️ 未找到 user_id={target_user_id} 的用户，正在自动创建...")
            user = models.User(
                user_id=target_user_id,
                username=f"user_{target_user_id}", # 自动生成一个用户名
                password="1234",
                avatar=""
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        print(f"✅ 将注入数据到用户: {user.username} (ID: {user.user_id})")
        # 3. 循环插入数据
        success_count = 0
        for item_data in local_items:
            filename = item_data.get("filename", "")
            if not filename:
                print(f"   [跳过] 数据缺失文件名: {item_data.get('name')}")
                continue

            # 3.1 校验图片是否存在 (不再复制，只是检查)
            image_disk_path = os.path.join(TARGET_DIR, filename)
            if not os.path.exists(image_disk_path):
                print(f"   [警告] 图片缺失: {filename} (在 static/uploads/items 下没找到)")
                # 你可以选择 continue 跳过，或者允许无图插入
                # continue 

            # 构造数据库存储的 URL
            db_image_url = f"/static/uploads/items/{filename}"

            # 3.2 查找分类
            category = db.query(models.Category).filter(models.Category.category_type == item_data["category"]).first()
            if not category:
                print(f"   [跳过] 未知分类: {item_data['category']}")
                continue

            # 3.3 查重 (防止重复运行)
            exists = db.query(models.ClothingItem).filter(
                models.ClothingItem.name == item_data["name"],
                models.ClothingItem.user_id == user.user_id
            ).first()
            
            if exists:
                print(f"   [已存在] {item_data['name']}")
                continue

            # 3.4 写入数据库
            new_item = models.ClothingItem(
                user_id=user.user_id,
                category_id=category.category_id,
                name=item_data["name"],
                color=item_data.get("color"),
                season=item_data.get("season"),
                style=item_data.get("style"),
                price=item_data.get("price"),
                image_url=db_image_url,

             #   purchase_date=datetime.now().date(),
                purchase_date=item_data.get("purchase_date") or datetime.now().date(),
                created_at=datetime.now(),
                brand = item_data.get("brand"),  # 读取品牌
                material = item_data.get("material"),  # 读取材质
                occasion = item_data.get("occasion"),  # 读取场合
                notes = item_data.get("notes"),  # 读取备注
            )
            db.add(new_item)
            db.flush()

            # 3.5 关联标签
            if "tags" in item_data and isinstance(item_data["tags"], list):
                for tag_name in item_data["tags"]:
                    tag = db.query(models.Tag).filter(models.Tag.tag_name == tag_name).first()
                    if tag:
                        new_item.tags.append(tag)
            
            print(f"   [成功] 入库: {new_item.name}")
            success_count += 1

        db.commit()
        print(f"\n✅ 操作完成！成功入库 {success_count} 条数据。")

    except Exception as e:
        print(f"❌ 发生异常: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    inject_data()