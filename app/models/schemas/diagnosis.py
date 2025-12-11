from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class SeverityLevel(str, Enum):
    NORMAL = "正常"
    MILD = "轻度"
    MODERATE = "中度"
    SEVERE = "重度"


class MeibomianImageBase(BaseModel):
    """睑板腺拍摄图片信息"""
    image_url: str = Field(..., description="图片存储路径或URL")
    device_model: Optional[str] = Field(None, description="拍摄设备型号")
    eye_side: str = Field(..., pattern="^(Left|Right)$", description="左眼或右眼")


class DiagnosisResult(BaseModel):
    """AI模型分析结果"""
    atrophy_rate: float = Field(..., description="睑板腺萎缩率 (0.0-1.0)")
    tortuosity_index: Optional[float] = Field(None, description="血管/腺体迂曲度指数")
    severity: SeverityLevel = Field(..., description="AI判定的严重程度")
    ai_confidence: float = Field(..., description="模型置信度")


class DiagnosisCreate(BaseModel):
    patient_id: str
    doctor_id: str
    chief_complaint: str = Field(..., description="主诉，如：眼干、异物感")
    # 图片上传后，由后端生成 image info


class DiagnosisInDB(BaseModel):
    id: str = Field(..., alias="_id")
    patient_id: str
    doctor_id: str

    # 图片信息
    images: List[MeibomianImageBase] = []

    # AI 分析结果 (分析完成后填充)
    ai_analysis: Optional[DiagnosisResult] = None

    # 医生最终修正诊断 (Human-in-the-loop)
    doctor_diagnosis: Optional[SeverityLevel] = None
    doctor_notes: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        populate_by_name = True