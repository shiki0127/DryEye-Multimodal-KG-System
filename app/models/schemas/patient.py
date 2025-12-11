from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum


# 定义性别枚举
class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


# 定义云南的主要地区枚举（用于后续关联 GIS 数据）
class YunnanRegion(str, Enum):
    KUNMING = "昆明"
    DALI = "大理"
    LIJIANG = "丽江"
    XISHUANGBANNA = "西双版纳"
    QUJING = "曲靖"
    YUXI = "玉溪"
    HONGHE = "红河"
    WENSHAN = "文山"
    PUER = "普洱"
    BAOSHAN = "保山"
    ZHAOTONG = "昭通"
    LINCANG = "临沧"
    CHUXIONG = "楚雄"
    DEHONG = "德宏"
    NUJIANG = "怒江"
    DIQING = "迪庆"


class PatientBase(BaseModel):
    name: str = Field(..., example="张三", description="病人姓名")
    gender: Gender = Field(..., description="性别")
    age: int = Field(..., gt=0, lt=120, description="年龄")
    phone: str = Field(..., description="联系电话")
    location: YunnanRegion = Field(..., description="居住地区，用于关联地理环境数据")

    # 生活习惯调查 (干眼症风险因素)
    screen_time_hours: float = Field(0, description="日均屏幕使用时间(小时)")
    has_contact_lenses: bool = Field(False, description="是否佩戴隐形眼镜")
    smoking_history: bool = Field(False, description="是否有吸烟史")
    makeup_frequency: str = Field("从不", description="眼部化妆频率")


class PatientCreate(PatientBase):
    """创建病人时需要的字段"""
    pass


class PatientUpdate(BaseModel):
    """更新病人时允许修改的字段（全部可选）"""
    name: Optional[str] = None
    age: Optional[int] = None
    location: Optional[YunnanRegion] = None
    screen_time_hours: Optional[float] = None
    # ... 其他字段按需添加


class PatientInDB(PatientBase):
    """数据库中存储的完整结构"""
    id: str = Field(..., alias="_id", description="MongoDB ObjectId")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        populate_by_name = True