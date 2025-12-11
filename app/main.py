from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.db.mongodb import connect_to_mongo, close_mongo_connection
from app.db.neo4j import neo4j_db
from app.api.v1.api import api_router

# 定义生命周期事件：启动时连接数据库，关闭时断开
@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup ---
    await connect_to_mongo()
    neo4j_db.connect()
    yield
    # --- Shutdown ---
    await close_mongo_connection()
    neo4j_db.close()

def create_application() -> FastAPI:
    application = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        description="云南干眼症多模态智慧诊疗与知识图谱系统后端接口",
        lifespan=lifespan  # 注册生命周期
    )

    # 设置跨域请求 (CORS)
    origins = [
        "http://localhost",
        "http://localhost:8080",
        "http://localhost:3000",
        "*"
    ]

    application.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 注册 API 路由
    application.include_router(api_router, prefix=settings.API_V1_STR)

    return application

app = create_application()

@app.get("/")
async def root():
    return {
        "message": "Welcome to DryEye Knowledge System API",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "app_name": settings.PROJECT_NAME
    }