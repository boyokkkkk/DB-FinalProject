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