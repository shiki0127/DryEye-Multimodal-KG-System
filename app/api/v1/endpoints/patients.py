from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_patients(skip: int = 0, limit: int = 100):
    # TODO: 从 MongoDB 获取患者列表
    return [{"patient_id": "P001", "name": "张三", "age": 45, "region": "云南迪庆"}]

@router.post("/")
async def create_patient(patient: dict):
    # TODO: 写入 MongoDB 并同步创建 Neo4j 的 (Patient) 节点
    return {"msg": "患者创建成功", "patient_id": "P002"}

@router.get("/{patient_id}")
async def get_patient_detail(patient_id: str):
    return {"patient_id": patient_id, "name": "李四", "details": "..."}