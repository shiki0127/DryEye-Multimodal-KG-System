from fastapi import APIRouter, Body, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from app.db.mongodb import get_database
from app.services.llm_service import llm_service

router = APIRouter()


@router.post("/ask")
async def ask_ai_doctor(
        patient_id: str = Body(..., embed=True),
        question: str = Body(..., embed=True),
        db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    智慧对话接口：结合病人病历向 AI 提问
    例如："这位病人的干眼症属于什么类型？建议如何治疗？"
    """
    # 1. 获取病人上下文数据
    if not ObjectId.is_valid(patient_id):
        raise HTTPException(status_code=400, detail="Invalid Patient ID")

    patient = await db["patients"].find_one({"_id": ObjectId(patient_id)})
    diagnosis_records = await db["diagnosis"].find({"patient_id": patient_id}).to_list(length=5)

    if not patient:
        return {"answer": "找不到该病人档案，无法分析。"}

    # 2. 拼接上下文 (RAG 的简易版)
    context = f"""
    病人姓名: {patient.get('name')}
    年龄: {patient.get('age')}
    居住地: {patient.get('location')}
    生活习惯: 屏幕时间 {patient.get('screen_time_hours')}小时, 化妆频率 {patient.get('makeup_frequency')}
    历史诊断记录数: {len(diagnosis_records)}
    最近一次主诉: {diagnosis_records[0].get('chief_complaint') if diagnosis_records else '无'}
    """

    # 3. 调用 LLM
    answer = await llm_service.chat_completion(question, context)

    return {"answer": answer}