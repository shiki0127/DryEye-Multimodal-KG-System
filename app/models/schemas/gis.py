from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


# 定义云南主要地区枚举 (与和风天气城市ID对应)
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
    DIQING = "迪庆"  # 香格里拉


class EnvironmentData(BaseModel):
    """环境因子数据模型 (返回给前端的数据结构)"""
    region: YunnanRegion = Field(..., description="云南地区")
    date: str = Field(..., description="日期 YYYY-MM-DD")

    # 核心环境因子 (干眼症相关)
    altitude: float = Field(..., description="海拔高度 (米) - 静态数据")
    humidity: float = Field(..., description="平均相对湿度 (%) - 实时API获取")
    temperature: float = Field(..., description="平均气温 (摄氏度) - 实时API获取")
    uv_index: Optional[float] = Field(None, description="紫外线指数 - 模拟或API高级版获取")
    sunlight_duration: Optional[float] = Field(None, description="日照时长 (小时)")

    class Config:
        populate_by_name = True