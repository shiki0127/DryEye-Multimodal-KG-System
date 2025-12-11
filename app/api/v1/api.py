from fastapi import APIRouter
from app.api.v1.endpoints import patients, diagnosis, gis, graph

api_router = APIRouter()

# 注册病人管理模块
api_router.include_router(patients.router, prefix="/patients", tags=["Patients (病人管理)"])

# 注册诊断模块 (新增)
api_router.include_router(diagnosis.router, prefix="/diagnosis", tags=["Diagnosis (辅助诊断)"])

# 注册地理信息模块 (新增)
api_router.include_router(gis.router, prefix="/gis", tags=["GIS (地理环境)"])

# 后续添加其他模块：
api_router.include_router(graph.router, prefix="/graph", tags=["Knowledge Graph (知识图谱)"])