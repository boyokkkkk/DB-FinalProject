from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from opengauss_sqlalchemy.psycopg2 import OpenGaussDialect_psycopg2
from sqlalchemy.dialects import registry
from sqlalchemy.engine import Connection
import re
import os
from urllib.parse import quote_plus


registry.register(
    "opengauss.psycopg2",
    "opengauss_sqlalchemy.psycopg2",
    "OpenGaussDialect_psycopg2"
)

DB_USER = "dbuser"
DB_PASS = "Cby@1234"
encoded_password = quote_plus(DB_PASS)
DB_HOST = "127.0.0.1"
DB_PORT = "15432"
DB_NAME = "finalpro_db"
SQLALCHEMY_DATABASE_URL = f"opengauss://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
print(f"{SQLALCHEMY_DATABASE_URL}")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    echo=True
)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_database():
    """初始化数据库表结构"""
    try:
        # 检查表是否存在
        with engine.connect() as conn:
            print("开始初始化数据库表结构...")
            
            # 读取SQL文件
            sql_file_path = os.path.join(os.path.dirname(__file__), '../sql/categories.sql')
            
            if not os.path.exists(sql_file_path):
                # 如果文件不存在，创建默认的初始化SQL
                print(f"SQL文件不存在: {sql_file_path}")
            else:
                with open(sql_file_path, 'r', encoding='utf-8') as f:
                    sql_script = f.read()
                
                # 按分号分割SQL语句并执行
                statements = [stmt.strip() for stmt in sql_script.split(';') if stmt.strip()]
                
                for statement in statements:
                    if statement:  # 跳过空语句
                        try:
                            conn.execute(text(statement))
                            print(f"执行SQL: {statement[:50]}...")  # 只打印前50个字符
                        except Exception as e:
                            print(f"执行SQL语句时出错: {e}")
                            print(f"问题语句: {statement[:100]}...")
                
                conn.commit()
                print("数据库初始化完成！")
                
    except Exception as e:
        print(f"数据库初始化过程中出错: {e}")
        raise

# 当直接运行此文件时初始化数据库
if __name__ == "__main__":
    init_database()