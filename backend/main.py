import os
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from database import engine, Base
from routers.user_router import router as user_router
from routers.outfit_router import router as outfit_router
from routers.upload_router import router as upload_router
from routers import wishlist
import models
from routers import closet

# ===================== 1. 配置日志 =====================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("DB-FinalProject")

# ===================== 2. 数据库初始化 =====================
Base.metadata.create_all(bind=engine)

# ===================== 3. 创建FastAPI应用 =====================
app = FastAPI(title="DbFinalProject Backend API", debug=True)

# ===================== 4. 跨域中间件 =====================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # 允许任何前端端口访问
    allow_credentials=True,
    allow_methods=["*"],  # 允许 GET, POST, PUT, DELETE 等所有方法
    allow_headers=["*"],  # 允许所有 Header
)

class ForceCORSHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["Access-Control-Allow-Origin"] = "http://localhost:5173"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "*"
        return response

app.add_middleware(ForceCORSHeadersMiddleware)

# ===================== 5. 静态文件配置 =====================
if not os.path.exists("static"):
    os.makedirs("static")
app.mount("/static", StaticFiles(directory="static"), name="static")

# ===================== 6. 注册路由 =====================
app.include_router(user_router)
app.include_router(closet.router)
app.include_router(outfit_router)
app.include_router(wishlist.router)
app.include_router(upload_router)


# ===================== 7. 根路由 =====================
@app.get("/")
def read_root():
    return {"message": "Welcome to the DbFinalProject Backend API"}


# ===================== 8. 全局异常处理器（核心：捕获422错误并打印详情） =====================
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """捕获所有请求参数校验错误（422），打印详细信息"""
    # 1. 读取请求体（如果是JSON/表单）
    try:
        request_body = await request.json()
    except Exception:
        try:
            request_body = await request.form()
        except Exception:
            request_body = "无法解析请求体（非JSON/表单格式）"

    # 2. 打印详细错误日志（控制台可见）
    logger.error(
        f"\n===== 请求参数校验失败（422）=====\n"
        f"请求路径: {request.url}\n"
        f"请求方法: {request.method}\n"
        f"请求体: {request_body}\n"
        f"校验错误详情: {exc.errors()}\n"
        f"====================================\n"
    )

    # 3. 返回友好的错误响应给前端
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),  # 具体的校验错误（字段+原因）
            "body": request_body,  # 客户端发送的原始请求体
            "message": "请求参数校验失败，请检查字段类型/必填项/取值范围"
        },
    )


# ===================== 9. 通用异常处理器（捕获其他500错误） =====================
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """捕获所有未处理的异常，打印详细堆栈"""
    logger.error(
        f"\n===== 服务器内部错误（500）=====\n"
        f"请求路径: {request.url}\n"
        f"请求方法: {request.method}\n"
        f"异常类型: {type(exc).__name__}\n"
        f"异常信息: {str(exc)}\n"
        f"====================================\n",
        exc_info=True  # 打印完整的堆栈跟踪
    )
    return JSONResponse(
        status_code=500,
        content={
            "message": "服务器内部错误，请查看后端日志",
            "error": str(exc)
        },
    )


# ===================== 10. 启动服务器 =====================
if __name__ == "__main__":
    import uvicorn

    # 启动时开启日志（uvicorn的日志也会输出）
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"  # uvicorn日志级别
    )