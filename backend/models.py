from sqlalchemy import (
    Column, Integer, String, Float, Text, Date,
    ForeignKey, DateTime, Table, UniqueConstraint
)
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
    username = Column(String(50), nullable=False)
    password = Column(String(100), nullable=False)
    create_time = Column(DateTime, default=datetime.now)

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