from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


# --- 枚举定义 (规范化输入) ---
class BooleanChoice(str, Enum):
    YES = "是"
    NO = "否"


class EyeSide(str, Enum):
    LEFT = "OS"
    RIGHT = "OD"
    BOTH = "OU"


# --- 子模型 1: 生活习惯与基础信息 (问卷部分) ---
class LifestyleInfo(BaseModel):
    # 对应 CSV: 职业, 教育程度, 吸烟史, 饮酒史, 饮食习惯...
    occupation: Optional[str] = Field(None, description="职业")
    education_level: Optional[str] = Field(None, description="教育程度")
    smoking_history: Optional[str] = Field(None, description="吸烟史")
    drinking_history: Optional[str] = Field(None, description="饮酒史")
    diet_habit: Optional[str] = Field(None, description="饮食习惯(清淡/油腻/辛辣)")
    daily_outdoor_hours: float = Field(0, description="每日户外活动时间(小时)")
    daily_screen_hours: float = Field(0, description="每天看手机/电脑时间(小时)")
    daily_sleep_hours: float = Field(0, description="每日睡眠时间(小时)")


# --- 子模型 2: 全身疾病史 (对应 CSV: 全身疾病...) ---
class SystemicHistory(BaseModel):
    has_hypertension: bool = Field(False, description="高血压")
    has_diabetes: bool = Field(False, description="糖尿病")
    has_heart_disease: bool = Field(False, description="心脏病")
    has_kidney_disease: bool = Field(False, description="肾病")
    has_rheumatic: bool = Field(False, description="风湿免疫相关疾病")
    has_thyroid: bool = Field(False, description="甲状腺疾病")
    has_facial_paralysis: bool = Field(False, description="面神经麻痹")
    other_systemic_disease: Optional[str] = Field(None, description="其他全身疾病名称")


# --- 子模型 3: 用药史 (对应 CSV: 长期用药...) ---
class MedicationHistory(BaseModel):
    use_antihypertensive: bool = Field(False, description="降压药")
    use_lipid_lowering: bool = Field(False, description="降脂药")
    use_hypoglycemic: bool = Field(False, description="降糖药")
    use_hormone: bool = Field(False, description="激素类")
    use_immunosuppressant: bool = Field(False, description="免疫抑制剂")
    use_sleeping_pills: bool = Field(False, description="安眠药")
    other_medication: Optional[str] = Field(None, description="其他长期用药")


# --- 子模型 4: 眼部病史 (对应 CSV: 眼部疾病, 手术, 滴眼液...) ---
class OcularHistory(BaseModel):
    eye_disease_name: Optional[str] = Field(None, description="眼部疾病名称")
    eye_surgery_name: Optional[str] = Field(None, description="眼部手术名称")
    eye_drops_usage: Optional[str] = Field(None, description="近3个月使用滴眼液名称")
    eye_infection_history: Optional[str] = Field(None, description="近3个月眼部感染史")
    wear_glasses: bool = Field(False, description="是否佩戴框架眼镜")
    wear_contact_lenses: bool = Field(False, description="是否佩戴隐形眼镜")


# --- 子模型 5: OSDI 干眼症状量表 (对应 CSV: 怕光, 疼痛...) ---
class OSDIScale(BaseModel):
    photophobia: int = Field(..., description="怕光/刺眼 (0-4分)")
    grittiness: int = Field(..., description="异物感/沙子感 (0-4分)")
    pain: int = Field(..., description="眼睛疼痛 (0-4分)")
    blurred_vision: int = Field(..., description="视力波动 (0-4分)")
    poor_vision: int = Field(..., description="视力差 (0-4分)")
    reading_difficulty: int = Field(..., description="读书写字困难 (0-4分)")
    night_driving_difficulty: int = Field(..., description="夜间开车困难 (0-4分)")
    screen_difficulty: int = Field(..., description="看电脑困难 (0-4分)")
    tv_difficulty: int = Field(..., description="看电视困难 (0-4分)")
    wind_discomfort: int = Field(..., description="刮风时不适 (0-4分)")
    dry_env_discomfort: int = Field(..., description="干燥环境不适 (0-4分)")
    ac_discomfort: int = Field(..., description="空调房不适 (0-4分)")

    total_score: float = Field(..., description="OSDI 总分 (由前端计算或后端计算)")


# --- 子模型 6: 临床体征数据 (对应 CSV: 临床体征数据部分) ---
class ClinicalSigns(BaseModel):
    # 视力
    od_vision: Optional[float] = Field(None, description="右眼(OD)视力")
    os_vision: Optional[float] = Field(None, description="左眼(OS)视力")

    # 裂隙灯检查
    conjunctival_congestion: Optional[str] = Field(None, description="结膜充血情况")
    corneal_staining_score: Optional[float] = Field(None, description="角膜荧光素染色评分")

    # 干眼专项
    but_od: Optional[float] = Field(None, description="右眼泪膜破裂时间(BUT)")
    but_os: Optional[float] = Field(None, description="左眼泪膜破裂时间(BUT)")
    schirmer_od: Optional[float] = Field(None, description="右眼泪液分泌试验(mm/5min)")
    schirmer_os: Optional[float] = Field(None, description="左眼泪液分泌试验(mm/5min)")

    # 睑板腺 (结合你的 U-Net 模型)
    meibomian_loss_rate: Optional[float] = Field(None, description="睑板腺缺失率(%)")
    meibomian_status: Optional[str] = Field(None, description="睑板腺开口状态")


# --- 主模型：完整临床记录 ---
class ClinicalRecordCreate(BaseModel):
    patient_id: str = Field(..., description="关联的病人ID")
    doctor_id: str = Field(..., description="录入医生ID")
    record_date: str = Field(..., description="记录日期 YYYY-MM-DD")

    # 嵌套各个模块
    lifestyle: LifestyleInfo
    systemic_history: SystemicHistory
    medication_history: MedicationHistory
    ocular_history: OcularHistory
    osdi_data: OSDIScale
    clinical_signs: ClinicalSigns

    # 诊断结论
    diagnosis_conclusion: str = Field(..., description="医生最终诊断")
    treatment_plan: Optional[str] = Field(None, description="治疗方案")


class ClinicalRecordInDB(ClinicalRecordCreate):
    id: str = Field(..., alias="_id")
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        populate_by_name = True