# backend/seed_data.py

from database import SessionLocal
import models
import security
from sqlalchemy.orm import Session

def seed_data():
    db = SessionLocal()
    try:
        print("🚀 开始生成测试数据...")

        # ==========================================
        # 1. 确保有一个测试用户
        # ==========================================
        # 您可以使用这个账号登录：用户名 test / 密码 123456
        test_username = "cby"
        test_password = "1234"
        
        user = db.query(models.User).filter(models.User.username == test_username).first()
        if not user:
            print(f"Creating user: {test_username} ...")
            # 使用 security 模块加密密码，确保能成功登录
            hashed_pwd = security.get_password_hash(test_password)
            user = models.User(username=test_username, password=hashed_pwd, avatar="")
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            print(f"User '{test_username}' already exists. ID: {user.user_id}")
            
        user_id = user.user_id

        # ==========================================
        # 2. 插入测试单品 (Items)
        # ==========================================
        # 对应前端的分类: Top, Bottom, Shoes, Accessory
        items_data = [
            {
                "name": "经典白T恤", 
                "category": "Top", 
                "image_url": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?auto=format&fit=crop&w=500&q=60", 
                "season": "Summer", 
                "style": "Casual"
            },
            {
                "name": "复古牛仔裤", 
                "category": "Bottom", 
                "image_url": "https://images.unsplash.com/photo-1542272454315-4c01d7abdf4a?auto=format&fit=crop&w=500&q=60", 
                "season": "All", 
                "style": "Casual"
            },
            {
                "name": "黑色运动鞋", 
                "category": "Shoes", 
                "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=500&q=60", 
                "season": "All", 
                "style": "Sport"
            },
            {
                "name": "羊毛大衣", 
                "category": "Top", 
                "image_url": "https://images.unsplash.com/photo-1591047139829-d91aecb6caea?auto=format&fit=crop&w=500&q=60", 
                "season": "Winter", 
                "style": "Formal"
            },
            {
                "name": "格纹围巾", 
                "category": "Accessory", 
                "image_url": "https://images.unsplash.com/photo-1520903920243-00d872a2d1c9?auto=format&fit=crop&w=500&q=60", 
                "season": "Winter", 
                "style": "Casual"
            }
        ]

        count = 0
        for item in items_data:
            # 防止重复插入同名商品
            exists = db.query(models.Item).filter(
                models.Item.name == item["name"], 
                models.Item.user_id == user_id
            ).first()
            
            if not exists:
                new_item = models.Item(
                    user_id=user_id,
                    name=item["name"],
                    category=item["category"],
                    image_url=item["image_url"],
                    season=item["season"],
                    style=item["style"]
                )
                db.add(new_item)
                count += 1
        
        db.commit()
        print(f"✅ 成功插入 {count} 件单品！")
        print(f"👉 请使用账号登录测试: {test_username} / {test_password}")
        
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()