from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.encoders import jsonable_encoder
from typing import List, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from enum import Enum  # <--- 新增导入

from app.db.mongodb import get_database
# 引入 Gender 和 YunnanRegion 是为了让 Swagger 显示下拉菜单
from app.models.schemas.patient import PatientCreate, PatientInDB, PatientUpdate, Gender, YunnanRegion

router = APIRouter()


# --- 新增：眼部化妆频率枚举 ---
class MakeupFrequency(str, Enum):
    NEVER = "从不"
    OCCASIONALLY = "偶尔"
    OFTEN = "经常"
    DAILY = "每天"


@router.post("/", response_model=PatientInDB, status_code=status.HTTP_201_CREATED)
async def create_patient(
        # --- 改为 Form 表单输入，Swagger 会显示为输入框 ---
        name: str = Form(..., description="病人姓名", example="张三"),
        gender: Gender = Form(..., description="性别"),  # 会显示下拉框
        age: int = Form(..., gt=0, lt=120, description="年龄"),
        phone: str = Form(..., description="联系电话"),
        location: YunnanRegion = Form(..., description="居住地区"),  # 会显示下拉框

        # 风险因素 (选填)
        screen_time_hours: float = Form(0, description="日均屏幕使用时间(小时)"),
        has_contact_lenses: bool = Form(False, description="是否佩戴隐形眼镜"),
        smoking_history: bool = Form(False, description="是否有吸烟史"),
        # 修改这里：使用 MakeupFrequency 枚举，Swagger 会自动生成下拉菜单
        makeup_frequency: MakeupFrequency = Form(MakeupFrequency.NEVER, description="眼部化妆频率"),

        db: AsyncIOMotorDatabase = Depends(get_database),
) -> Any:
    """
    录入新病人信息 (表单模式)
    """
    # 1. 检查是否已存在 (按手机号)
    existing_patient = await db["patients"].find_one({"phone": phone})
    if existing_patient:
        raise HTTPException(
            status_code=400,
            detail="The patient with this phone number already exists."
        )

    # 2. 将表单数据封装回 Pydantic 模型 (为了复用校验逻辑)
    patient_in = PatientCreate(
        name=name,
        gender=gender,
        age=age,
        phone=phone,
        location=location,
        screen_time_hours=screen_time_hours,
        has_contact_lenses=has_contact_lenses,
        smoking_history=smoking_history,
        makeup_frequency=makeup_frequency
    )

    # 3. 准备插入数据
    patient_data = jsonable_encoder(patient_in)

    # 4. 插入 MongoDB
    new_patient = await db["patients"].insert_one(patient_data)

    # 5. 获取刚插入的完整文档
    created_patient = await db["patients"].find_one({"_id": new_patient.inserted_id})

    return created_patient


@router.get("/", response_model=List[PatientInDB])
async def read_patients(
        db: AsyncIOMotorDatabase = Depends(get_database),
        skip: int = 0,
        limit: int = 100
) -> Any:
    """
    获取病人列表 (分页)
    """
    patients = []
    cursor = db["patients"].find().skip(skip).limit(limit)
    async for doc in cursor:
        patients.append(doc)
    return patients


@router.get("/{patient_id}", response_model=PatientInDB)
async def read_patient(
        patient_id: str,
        db: AsyncIOMotorDatabase = Depends(get_database)
) -> Any:
    """
    根据 ID 获取病人详情
    """
    if not ObjectId.is_valid(patient_id):
        raise HTTPException(status_code=400, detail="Invalid ID format")

    patient = await db["patients"].find_one({"_id": ObjectId(patient_id)})

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    return patient


@router.put("/{patient_id}", response_model=PatientInDB)
async def update_patient(
        patient_id: str,
        patient_in: PatientUpdate,
        db: AsyncIOMotorDatabase = Depends(get_database)
) -> Any:
    """
    更新病人信息 (这里保持 JSON Body 即可，更新通常不需要填所有字段)
    """
    if not ObjectId.is_valid(patient_id):
        raise HTTPException(status_code=400, detail="Invalid ID format")

    patient = await db["patients"].find_one({"_id": ObjectId(patient_id)})
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    update_data = {k: v for k, v in patient_in.dict().items() if v is not None}

    if update_data:
        await db["patients"].update_one(
            {"_id": ObjectId(patient_id)},
            {"$set": update_data}
        )

    return await db["patients"].find_one({"_id": ObjectId(patient_id)})