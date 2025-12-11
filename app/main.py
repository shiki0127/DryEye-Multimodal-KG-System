from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

# 以后这里会导入具体的路由
# from app.api.v1.api import api_router

def create_application() -> FastAPI:
    application = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        description="云南干眼症多模态智慧诊疗与知识图谱系统后端接口"
    )

    # 设置跨域请求 (CORS)，允许前端访问
    origins = [
        "http://localhost",
        "http://localhost:8080",
        "http://localhost:3000", # 常见前端端口
        "*"                      # 开发阶段允许所有
    ]

    application.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 注册路由 (暂时注释，等写好路由文件再开启)
    # application.include_router(api_router, prefix=settings.API_V1_STR)

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
    return {"status": "ok", "db_mongo": "pending", "db_neo4j": "pending"}