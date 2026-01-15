import os
from sqlalchemy import text
from database import engine

def reset_tables():
    # 1. 计算 sql/init.sql 的绝对路径
    # 当前脚本在 backend/ 目录下，所以要向上一级 (..) 找 sql/init.sql
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sql_path = os.path.join(current_dir, '..', 'sql', 'init.sql')

    print(f"📂 正在读取 SQL 文件: {sql_path}")

    if not os.path.exists(sql_path):
        print("❌ 错误：找不到 init.sql 文件！请检查路径。")
        return

    # 2. 读取 SQL 内容
    with open(sql_path, "r", encoding="utf-8") as f:
        sql_content = f.read()

    print("🚀 开始重置数据库表...")

    # 3. 连接数据库并执行
    try:
        with engine.connect() as conn:
            # openGauss/Postgres 允许一次性执行多条语句 (DROP + CREATE)
            conn.execute(text(sql_content))
            conn.commit()
        print("✅ 数据库表重置成功！")
    except Exception as e:
        print(f"❌ 执行出错: {e}")

if __name__ == "__main__":
    reset_tables()