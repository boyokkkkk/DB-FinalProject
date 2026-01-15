# from fastapi import APIRouter, Depends
# from sqlalchemy.orm import Session
# from database import get_db
#
# router = APIRouter()
# @router.get("/")
# def read_users():
#     return [{"message": "List of users"}]

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
import models, schemas
import security
from fastapi import File, UploadFile
import os
import uuid
import shutil
# 创建路由
router = APIRouter(
    prefix="/api/user",
    tags=["User"]
)


# =======================
# 注册接口
# =======================
@router.post("/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # 检查用户名是否已存在
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="用户名已存在")

    hashed_password = security.get_password_hash(user.password)

    # 创建新用户
    new_user = models.User(
        username=user.username,
        password=hashed_password, 
        avatar=""
    )

    # 存入数据库
    db.add(new_user)
    db.commit()
    db.refresh(new_user)  # 刷新以获取自动生成的 user_id

    return new_user


# =======================
# 登录接口
# =======================
@router.post("/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    # 1. 查用户
    db_user = db.query(models.User).filter(models.User.username == user.username).first()

    # 2. 校验用户是否存在 & 密码是否正确
    if not db_user or not security.verify_password(user.password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )

    access_token = security.create_access_token(data={"sub": str(db_user.user_id)})

    # 3. 登录成功 (这里简单返回用户信息，正规做法是返回 Token)
    return {
        "msg": "登录成功",
        "code": 200,
        "data": {
            "token": access_token,
            "user_id": db_user.user_id,
            "username": db_user.username,
            "avatar": db_user.avatar
        }
    }


@router.put("/{user_id}", response_model=schemas.UserOut)
def update_user(user_id: int, user_update: schemas.UserUpdate, db: Session = Depends(get_db)):
    # 1. 查找用户
    db_user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 2. 如果修改了用户名，要检查是否和其他人重复
    if user_update.username and user_update.username != db_user.username:
        existing_user = db.query(models.User).filter(models.User.username == user_update.username).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="该用户名已被占用")
        db_user.username = user_update.username

    # 3. 更新其他字段
    if user_update.password:
        db_user.password = user_update.password  # 同样，实际项目中请记得加密

    if user_update.avatar is not None:
        db_user.avatar = user_update.avatar

    # 4. 提交保存
    db.commit()
    db.refresh(db_user)

    return db_user


# =======================
# 上传头像接口
# =======================
@router.post("/{user_id}/avatar")
async def upload_avatar(user_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    # 1. 检查用户是否存在
    db_user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 2. 准备保存路径
    # 确保 static/avatars 目录存在
    UPLOAD_DIR = "static/avatars"
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)

    # 3. 生成唯一文件名 (防止同名文件覆盖)
    # file.filename 比如是 "photo.jpg" -> 取后缀 ".jpg"
    file_extension = os.path.splitext(file.filename)[1]
    # 生成比如 "uuid-uuid-uuid.jpg"
    new_filename = f"{uuid.uuid4()}{file_extension}"

    # 完整保存路径: static/avatars/xxxx.jpg
    file_path = os.path.join(UPLOAD_DIR, new_filename)

    # 4. 保存文件到硬盘
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 5. 生成访问 URL
    avatar_url = f"/static/avatars/{new_filename}"

    # 6. 更新数据库
    db_user.avatar = avatar_url
    db.commit()
    db.refresh(db_user)

    return db_user
