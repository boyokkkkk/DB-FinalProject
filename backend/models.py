from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, UniqueConstraint, func
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

# class User(Base):
#     __tablename__ = "sys_user"
#
#     user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
#     username = Column(String(50), nullable=False)
#     password = Column(String(100), nullable=False)
#     create_time = Column(DateTime, default=datetime.now)
#
#

class User(Base):
    __tablename__ = "sys_user" # 对应数据库里的表名
    # 对应数据库里的字段
    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    avatar = Column(String(255), nullable=True)
    create_time = Column(DateTime(timezone=True), server_default=func.now()) # 创建时间