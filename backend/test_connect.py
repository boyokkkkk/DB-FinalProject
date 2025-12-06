# import psycopg2
# from psycopg2 import OperationalError

# DB_HOST = "127.0.0.1"
# DB_PORT = "15432"
# DB_NAME = "finalpro_db"
# DB_USER = "cby"
# DB_PASS = "Cby1234#"

# def test_raw_connection():
#     print(f"Trying to connect to openGauss using psycopg2...")
#     conn = None
#     try:
#         conn = psycopg2.connect(
#             host=DB_HOST,
#             port=DB_PORT,
#             dbname=DB_NAME,
#             user=DB_USER,
#             password=DB_PASS
#         )
 
#         cur = conn.cursor()
#         cur.execute("SELECT version();")
#         version = cur.fetchone()[0]
        
#         print("[Successful]")
#         print(f"[Version] {version}")
        
#     except OperationalError as e:
#         print("[Failed]")
#         print(f"Error: {e}")
        
#     except Exception as e:
#         print("Error: ")
#         print(e)
        
#     finally:
#         if conn:
#             conn.close()

# if __name__ == "__main__":
#     test_raw_connection()
import re
from urllib.parse import quote_plus
from sqlalchemy import create_engine, text
from configparser import ConfigParser
from sqlalchemy.dialects.postgresql import psycopg2
from sqlalchemy.dialects import registry


class OpenGaussDialect(psycopg2.PGDialect_psycopg2):
    # 这里可以添加 openGauss 特有的行为
    # 例如，修改某些 SQL 语句，添加特定的数据类型等
    pass


# 注册方言
registry.register(OpenGaussDialect, 'opengauss', 'opengauss+psycopg2')

# 现在，当您使用 'opengauss+psycopg2' 作为方言时，SQLAlchemy 将使用您的自定义方言
    # 创建配置解析器并读取INI文件
parser = ConfigParser()
parser.read('db.ini')

# 从INI文件中获取opengauss部分的参数
opengauss_config = parser['opengauss']
encoded_pwd=quote_plus(opengauss_config["password"])

# 构建数据库连接字符串
database_url = f'opengauss+psycopg2://{opengauss_config["user"]}:{encoded_pwd}@{opengauss_config["host"]}:{opengauss_config["port"]}/{opengauss_config["database"]}'

# 创建SQLAlchemy引擎
engine = create_engine(database_url)

# 使用引擎执行查询
with engine.connect() as connection:
    result = connection.execute(text("SELECT version()"))
    version = result.fetchone()[0]
    print('Server version:', version)