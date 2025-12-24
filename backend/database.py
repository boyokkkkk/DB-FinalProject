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

DB_USER = "cby"
DB_PASS = "Cby1234#"
DB_HOST = "127.0.0.1"
DB_PORT = "15432"
DB_NAME = "finalpro_db"
SQLALCHEMY_DATABASE_URL = f"opengauss+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
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