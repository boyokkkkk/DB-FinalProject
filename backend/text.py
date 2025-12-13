#!/usr/bin/python
import psycopg2

conn = psycopg2.connect(database="finalpro_db", user="dbuser", password="Cby@1234", host="127.0.0.1", port="15432")

cur = conn.cursor()

# 创建表COMPANY1
cur.execute('''CREATE TABLE COMPANY1
       (ID INT PRIMARY KEY     NOT NULL,
       NAME           TEXT    NOT NULL,
       AGE            INT     NOT NULL,
       ADDRESS        CHAR(50),
       SALARY         REAL);''')

# 插入数据
cur.execute("INSERT INTO COMPANY1 (ID,NAME,AGE,ADDRESS,SALARY) \
      VALUES (1, 'Paul', 32, 'California', 20000.00 )");

cur.execute("INSERT INTO COMPANY1 (ID,NAME,AGE,ADDRESS,SALARY) \
      VALUES (2, 'Allen', 25, 'Texas', 15000.00 )");

cur.execute("INSERT INTO COMPANY1 (ID,NAME,AGE,ADDRESS,SALARY) \
      VALUES (3, 'Teddy', 23, 'Norway', 20000.00 )");

cur.execute("INSERT INTO COMPANY1 (ID,NAME,AGE,ADDRESS,SALARY) \
      VALUES (4, 'Mark', 25, 'Rich-Mond ', 65000.00 )");

# 查询结果
cur.execute("SELECT id, name, address, salary  from COMPANY1")
rows = cur.fetchall()
for row in rows:
    print("ID = ", row[0])
    print("NAME = ", row[1])
    print("ADDRESS = ", row[2])
    print("SALARY = ", row[3])

conn.commit()
conn.close()
