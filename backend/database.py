from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from opengauss_sqlalchemy.psycopg2 import OpenGaussDialect_psycopg2
from sqlalchemy.dialects import registry
from sqlalchemy.engine import Connection
import re

# ----------------- openGauss 兼容性方言 -----------------
registry.register(
    "opengauss.psycopg2",
    "opengauss_sqlalchemy.psycopg2",
    "OpenGaussDialect_psycopg2"
)
# ----------------- 数据库连接配置 -----------------

DB_USER = "cby"
DB_PASS = "Cby1234#"
DB_HOST = "127.0.0.1"
DB_PORT = "15432"
DB_NAME = "finalpro_db"
SQLALCHEMY_DATABASE_URL = f"opengauss+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# 创建数据库引擎
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    echo=True
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 声明基类，所有 Model 都将继承这个类
Base = declarative_base()

# 依赖项：获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()