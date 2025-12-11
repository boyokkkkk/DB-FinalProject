from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers.user_router import router as user_router
import os
import models

Base.metadata.create_all(bind=engine)
app = FastAPI(title="DbFinalProject Backend API")

# origins = [
#     "http://127.0.0.1:8000",
#     "http://localhost:8000",
#     "null",
# ]
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

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

# app.include_router(user_router, prefix="/api/users", tags=["Users"])
app.include_router(user_router)
@app.get("/")
def read_root():
    return {"message": "Welcome to the DbFinalProject Backend API"}
