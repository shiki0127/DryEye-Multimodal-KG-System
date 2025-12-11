import os
import shutil
import uuid
from datetime import datetime
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from app.db.mongodb import get_database
from app.models.schemas.diagnosis import DiagnosisInDB, DiagnosisCreate, MeibomianImageBase, DiagnosisResult, \
    SeverityLevel

router = APIRouter()

# 图片存储目录
UPLOAD_DIR = "uploads/images"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload", response_model=DiagnosisInDB, status_code=status.HTTP_201_CREATED)
async def upload_diagnosis_image(
        patient_id: str = Form(...),
        doctor_id: str = Form(...),
        chief_complaint: str = Form(...),
        eye_side: str = Form(..., description="Left or Right"),
        file: UploadFile = File(...),
        db: AsyncIOMotorDatabase = Depends(get_database)
) -> Any:
    """
    上传眼部照片并创建初步诊断记录
    """
    # 1. 验证 Patient ID 是否有效
    if not ObjectId.is_valid(patient_id):
        raise HTTPException(status_code=400, detail="Invalid Patient ID")

    patient = await db["patients"].find_one({"_id": ObjectId(patient_id)})
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # 2. 保存文件到本地
    # 生成唯一文件名: uuid + 原始扩展名
    file_ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 3. 构造数据库记录
    # 注意：这里我们构造一个 DiagnosisInDB 结构存入 Mongo
    image_info = MeibomianImageBase(
        image_url=file_path,
        device_model="Default-Device",  # 实际可从前端获取
        eye_side=eye_side
    )

    diagnosis_doc = {
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "images": [image_info.dict()],
        "chief_complaint": chief_complaint,
        "created_at": datetime.now(),
        "ai_analysis": None,  # 暂时为空，等待分析
        "doctor_diagnosis": None
    }

    new_diagnosis = await db["diagnosis"].insert_one(diagnosis_doc)
    created_diagnosis = await db["diagnosis"].find_one({"_id": new_diagnosis.inserted_id})

    return created_diagnosis


@router.post("/{diagnosis_id}/analyze", response_model=DiagnosisInDB)
async def analyze_diagnosis(
        diagnosis_id: str,
        db: AsyncIOMotorDatabase = Depends(get_database)
) -> Any:
    """
    触发 AI 进行诊断分析 (Mock 模拟)
    """
    if not ObjectId.is_valid(diagnosis_id):
        raise HTTPException(status_code=400, detail="Invalid ID")

    diagnosis = await db["diagnosis"].find_one({"_id": ObjectId(diagnosis_id)})
    if not diagnosis:
        raise HTTPException(status_code=404, detail="Diagnosis record not found")

    # --- 这里是未来接入 U-net 模型的地方 ---
    # 目前模拟一个随机结果
    mock_ai_result = DiagnosisResult(
        atrophy_rate=0.35,  # 假设萎缩率 35%
        tortuosity_index=1.2,
        severity=SeverityLevel.MODERATE,  # 中度
        ai_confidence=0.92
    )
    # ------------------------------------

    await db["diagnosis"].update_one(
        {"_id": ObjectId(diagnosis_id)},
        {"$set": {"ai_analysis": mock_ai_result.dict()}}
    )

    return await db["diagnosis"].find_one({"_id": ObjectId(diagnosis_id)})


@router.get("/patient/{patient_id}", response_model=List[DiagnosisInDB])
async def read_patient_history(
        patient_id: str,
        db: AsyncIOMotorDatabase = Depends(get_database)
) -> Any:
    """获取某位病人的所有诊断历史"""
    if not ObjectId.is_valid(patient_id):
        raise HTTPException(status_code=400, detail="Invalid Patient ID")

    history = []
    cursor = db["diagnosis"].find({"patient_id": patient_id})
    async for doc in cursor:
        history.append(doc)
    return history