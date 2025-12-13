import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers.user_router import router as user_router
from routers.outfit_router import  router as outfit_router
import models
from routers import closet  # 导入路由

Base.metadata.create_all(bind=engine)
app = FastAPI(title="DbFinalProject Backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许任何前端端口访问
    allow_credentials=True,
    allow_methods=["*"],  # 允许 GET, POST, PUT, DELETE 等所有方法
    allow_headers=["*"],  # 允许所有 Header
)



if not os.path.exists("static"):
    os.makedirs("static")
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(user_router)
app.include_router(closet.router)
app.include_router(outfit_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the DbFinalProject Backend API"}

# 关键：启动服务器的代码
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
