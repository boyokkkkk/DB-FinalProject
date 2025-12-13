from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, UniqueConstraint, func, Float, Date, DateTime, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from database import Base

clothing_tags = Table(
    'clothing_tags',
    Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('item_id', Integer, ForeignKey('clothing_items.item_id', ondelete='CASCADE')),
    Column('tag_id', Integer, ForeignKey('tags.tag_id', ondelete='CASCADE')),
    UniqueConstraint('item_id', 'tag_id', name='uq_clothing_tags')
)

class User(Base):
    __tablename__ = "sys_user"

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    avatar = Column(String(255), nullable=True)
    create_time = Column(DateTime(timezone=True), server_default=func.now())

    clothing_items = relationship("ClothingItem", back_populates="user", cascade="all, delete-orphan")

class Category(Base):
    __tablename__ = 'categories'
    
    category_id = Column(Integer, primary_key=True, index=True)
    category_name = Column(String(50), nullable=False)
    category_type = Column(String(20), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    clothes = relationship("ClothingItem", back_populates="category")

class ClothingItem(Base):
    __tablename__ = 'clothing_items'
    
    item_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('sys_user.user_id', ondelete='CASCADE'), nullable=False)
    category_id = Column(Integer, ForeignKey('categories.category_id', ondelete='CASCADE'))
    name = Column(String(100), nullable=False)
    brand = Column(String(100))
    color = Column(String(50))
    season = Column(String(20))
    occasion = Column(String(50))
    style = Column(String(50))
    material = Column(String(100))
    purchase_date = Column(Date)
    price = Column(Float)
    image_url = Column(String(500))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="clothing_items")
    category = relationship("Category", back_populates="clothes")
    tags = relationship("Tag", secondary=clothing_tags, back_populates="clothes")

class Tag(Base):
    __tablename__ = 'tags'
    
    tag_id = Column(Integer, primary_key=True, index=True)
    tag_name = Column(String(50), nullable=False)
    tag_type = Column(String(20), nullable=False)
    
    clothes = relationship("ClothingItem", secondary=clothing_tags, back_populates="tags")

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
    create_time = Column(DateTime, default=datetime.now)