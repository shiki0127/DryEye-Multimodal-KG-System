from fastapi import APIRouter
from app.api.v1.endpoints import patients, diagnosis, gis, graph, login, chat

api_router = APIRouter()

# 1. 认证模块 (Auth)
# 包含 /login/access-token 和 /register，通常不需要统一的前缀 /auth，直接暴露在根路径或按需加
api_router.include_router(login.router, tags=["Auth (认证与登录)"])

# 2. 智慧对话模块 (AI Chat)
api_router.include_router(chat.router, prefix="/chat", tags=["AI Chat (智慧医生对话)"])

# 3. 核心业务模块
api_router.include_router(patients.router, prefix="/patients", tags=["Patients (病人管理)"])
api_router.include_router(diagnosis.router, prefix="/diagnosis", tags=["Diagnosis (辅助诊断)"])
api_router.include_router(gis.router, prefix="/gis", tags=["GIS (地理环境)"])
api_router.include_router(graph.router, prefix="/graph", tags=["Knowledge Graph (知识图谱)"])