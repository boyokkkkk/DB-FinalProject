import os
import shutil
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException

router = APIRouter(
    prefix="/api/upload",
    tags=["upload"]
)

# 确保上传目录存在
BASE_UPLOAD_DIR = "static/uploads"
if not os.path.exists(BASE_UPLOAD_DIR):
    os.makedirs(BASE_UPLOAD_DIR)

@router.post("/image")
async def upload_image(file: UploadFile = File(...), type: str = "item"):
    """
    通用图片上传接口:param type: 'item' (单品) 或 'outfit' (搭配截图)
    """
    try:
        filename = file.filename
        ext = os.path.splitext(filename)[1].lower()
        if ext not in [".jpg", ".jpeg", ".png", ".gif", ".webp"]:
            ext = ".jpg"

        # 2. 根据类型决定子目录
        if type == "outfit":
            subdir = "outfits"
        else:
            subdir = "items"
            
        target_dir = os.path.join(BASE_UPLOAD_DIR, subdir)
        
        # 确保目录存在
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        # 3. 生成唯一文件名
        unique_filename = f"{uuid.uuid4().hex}{ext}"
        file_path = os.path.join(target_dir, unique_filename)

        # 4. 保存文件
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 5. 返回 URL (注意路径包含子目录)
        return {"url": f"/static/uploads/{subdir}/{unique_filename}"}

    except Exception as e:
        print(f"上传失败: {e}")
        raise HTTPException(status_code=500, detail="文件上传失败")