from fastapi import APIRouter
from app.api.v1.endpoints import patients, diagnosis, gis, graph, login, chat, records

api_router = APIRouter()

# ==========================================
# 1. 认证与安全模块 (Auth)
# ==========================================
# 包含 /login/access-token 和 /register
api_router.include_router(login.router, tags=["Auth (认证与登录)"])

# ==========================================
# 2. 智慧对话模块 (AI Chat)
# ==========================================
# 包含 /chat/ask
api_router.include_router(chat.router, prefix="/chat", tags=["AI Chat (智慧医生对话)"])

# ==========================================
# 3. 核心业务模块
# ==========================================

# 病人管理 (增删改查)
api_router.include_router(patients.router, prefix="/patients", tags=["Patients (病人管理)"])

# 辅助诊断 (图片上传与 AI 分析)
api_router.include_router(diagnosis.router, prefix="/diagnosis", tags=["Diagnosis (辅助诊断)"])

# 临床问卷与体征 (新增: 对应那张大表格)
api_router.include_router(records.router, prefix="/records", tags=["Clinical Records (临床问卷与体征)"])

# 地理信息 (和风天气 API)
api_router.include_router(gis.router, prefix="/gis", tags=["GIS (地理环境)"])

# 知识图谱 (Neo4j 构建与可视化)
api_router.include_router(graph.router, prefix="/graph", tags=["Knowledge Graph (知识图谱)"])