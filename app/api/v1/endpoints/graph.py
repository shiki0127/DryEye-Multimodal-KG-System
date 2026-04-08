from fastapi import APIRouter

router = APIRouter()

@router.get("/visualization/{patient_id}")
async def get_graph_data(patient_id: str):
    # TODO: 执行 Cypher 查询 MATCH (p:Patient {id: $id})-[r]->(n) RETURN p, r, n
    # 模拟前端 ECharts 需要的节点和边格式
    nodes = [
        {"id": "0", "name": "张三", "category": "Patient"},
        {"id": "1", "name": "强紫外线", "category": "Environment"},
        {"id": "2", "name": "翼状胬肉", "category": "Disease"}
    ]
    links = [
        {"source": "0", "target": "1", "relation": "EXPOSED_TO"},
        {"source": "1", "target": "2", "relation": "INDUCES"}
    ]
    return {"nodes": nodes, "links": links}