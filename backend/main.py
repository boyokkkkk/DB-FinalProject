import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from database import init_database, engine, Base
from routers.user_router import router as user_router
import models
from routers import closet  # 导入路由

# init_database()

Base.metadata.create_all(bind=engine)
app = FastAPI(title="DbFinalProject Backend API")

origins = [
    "http://127.0.0.1:5173",
    "http://localhost:5173",
    "null",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # 输出到终端
    print("\n" + "=" * 60)
    print("❌ Pydantic 验证错误详情:")
    print("=" * 60)

    for i, error in enumerate(exc.errors(), 1):
        print(f"\n错误 #{i}:")
        print(f"  位置: {error.get('loc', [])}")
        print(f"  消息: {error.get('msg', '')}")
        print(f"  类型: {error.get('type', '')}")

    print(f"\n📦 接收到的原始数据:")
    print(f"{exc.body}")
    print("=" * 60 + "\n")

    # 返回给前端的响应
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "body": exc.body
        },
    )

if not os.path.exists("static"):
    os.makedirs("static")
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(user_router, prefix="/api/users", tags=["Users"])
app.include_router(closet.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the DbFinalProject Backend API"}

# 关键：启动服务器的代码
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)