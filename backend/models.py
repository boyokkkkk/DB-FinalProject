from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, UniqueConstraint, func, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "sys_user" # 瀵瑰簲鏁版嵁搴撻噷鐨勮〃鍚�
    # 瀵瑰簲鏁版嵁搴撻噷鐨勫瓧娈�
    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    avatar = Column(String(255), nullable=True)
    create_time = Column(DateTime(timezone=True), server_default=func.now()) # 鍒涘缓鏃堕棿

class Item(Base):
    __tablename__ = "item"

    item_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("sys_user.user_id"), nullable=False) # from user
    name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False) # top bottom shoes accessory
    image_url = Column(String(255), nullable=True)
    color = Column(String(50))
    season = Column(String(50))
    style = Column(String(50))
    purchase_date = Column(DateTime(timezone=True), nullable=True)
    create_time = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relations
    outfit_references = relationship("OutfitRef", back_populates="item")
    user = relationship("User")

class Outfit(Base):
    __tablename__ = "outfit"

    outfit_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("sys_user.user_id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    season = Column(String(50))
    style = Column(String(50))
    image_url = Column(String(255), nullable=True) # OutfitBoard Canvas
    create_time = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relations
    items = relationship("OutfitRef", back_populates="outfit", cascade="all, delete-orphan")
    user = relationship("User")

class OutfitRef(Base):
    __tablename__ = "outfit_ref"
    
    # Foreign Keys
    outfit_id = Column(Integer, ForeignKey("outfit.outfit_id"), primary_key=True)
    item_id = Column(Integer, ForeignKey("item.item_id"), primary_key=True)
    
    # OutfitBoard Canvas
    position_x = Column(Float, nullable=False, default=0.0)
    position_y = Column(Float, nullable=False, default=0.0)
    rotation = Column(Float, nullable=False, default=0.0)
    scale_x = Column(Float, nullable=False, default=1.0)
    scale_y = Column(Float, nullable=False, default=1.0)
    z_index = Column(Integer, nullable=False, default=0) # Layout

    # Relations
    outfit = relationship("Outfit", back_populates="items")
    item = relationship("Item", back_populates="outfit_references")