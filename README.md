## hsh 12.11
pip install python-multipart

请在前端项目根目录（frontend 文件夹下）运行：

npm install vue-cropper

npm install echarts

reset_db.py 可以执行init.sql 清空数据库并重新建新的空表

后端

cd backend

uvicorn main:app --reload

前端

cd frontend

npm run dev

## cby12.13
合了两个界面，分用户——涉及到前端的request.js、后端的security.py
搭配和衣橱两个界面还有细节要改
现在图片的处理逻辑有些问题

还是先运行后端的reset_db.py建表，保证数据库里面有这几张表
![alt text](README_images/image.png)
然后注册登录，保证有用户
![alt text](README_images/2.png)
后端uvicorn main:app --reload
前端npm run dev
可以使用使用数据库用户端或者类似下的辅助查看数据库的应用手动先插入单品验证（放在./sql/test_item.sql）
![alt text](README_images/3.png)

![alt text](README_images/4.png)
![alt text](README_images/5.png)