from fastapi import APIRouter, Depends
from typing import Any
from app.services.graph_builder import graph_service

router = APIRouter()

@router.post("/build", response_model=Any)
async def build_knowledge_graph() -> Any:
    """
    [触发] 全量构建知识图谱
    从 MongoDB 读取所有病人与诊断数据，写入 Neo4j
    """
    result = await graph_service.build_full_graph()
    return result

@router.get("/visualize", response_model=Any)
async def get_graph_visualization() -> Any:
    """
    [ECharts 专用] 获取知识图谱可视化数据
    返回格式: { nodes: [], links: [], categories: [] }
    """
    data = await graph_service.get_echarts_data()
    return data