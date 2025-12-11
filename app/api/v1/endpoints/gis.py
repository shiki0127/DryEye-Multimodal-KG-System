from typing import List, Any, Optional
import httpx
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query
from app.models.schemas.gis import EnvironmentData, YunnanRegion

router = APIRouter()

# ================= 配置区域 =================
QWEATHER_API_KEY = "c0192dec310c478e8783cdd99680557d"

# 和风天气 API 基础 URL (免费开发版使用 devapi)
QWEATHER_API_URL = "https://devapi.qweather.com/v7/weather/now"

# 云南各地区对应的和风天气 Location ID 映射表
# 这些 ID 是固定的，用于告诉 API 我们要查哪个城市
REGION_LOCATION_ID = {
    YunnanRegion.KUNMING: "101290101",
    YunnanRegion.DALI: "101290201",
    YunnanRegion.LIJIANG: "101291401",
    YunnanRegion.XISHUANGBANNA: "101291601",  # 景洪
    YunnanRegion.QUJING: "101290401",
    YunnanRegion.DIQING: "101291101",  # 香格里拉
    YunnanRegion.YUXI: "101290701",
    YunnanRegion.HONGHE: "101290301",  # 蒙自
    YunnanRegion.WENSHAN: "101290601",
    YunnanRegion.PUER: "101290501",
    YunnanRegion.BAOSHAN: "101290501",
    YunnanRegion.ZHAOTONG: "101291001",
    YunnanRegion.LINCANG: "101291301",
    YunnanRegion.CHUXIONG: "101290801",
    YunnanRegion.DEHONG: "101291501",  # 芒市
    YunnanRegion.NUJIANG: "101291201"  # 六库
}

# ================= 模拟数据区域 (兜底用) =================
# 即使 API 挂了，或者 Key 没填，系统也能通过这些数据正常运行
MOCK_GIS_DATA = {
    YunnanRegion.KUNMING: {
        "altitude": 1891, "humidity": 65.0, "temperature": 16.5, "uv_index": 8.0, "sunlight_duration": 7.5
    },
    YunnanRegion.DALI: {
        "altitude": 1976, "humidity": 58.0, "temperature": 15.1, "uv_index": 9.0, "sunlight_duration": 8.0
    },
    YunnanRegion.LIJIANG: {
        "altitude": 2400, "humidity": 55.0, "temperature": 13.0, "uv_index": 10.0, "sunlight_duration": 8.2
    },
    YunnanRegion.DIQING: {
        "altitude": 3280, "humidity": 45.0, "temperature": 5.4, "uv_index": 11.0, "sunlight_duration": 9.0
    },
    YunnanRegion.XISHUANGBANNA: {
        "altitude": 550, "humidity": 80.0, "temperature": 25.0, "uv_index": 6.0, "sunlight_duration": 6.5
    }
}


# ================= 核心逻辑 =================

async def fetch_real_weather(region: YunnanRegion) -> Optional[dict]:
    """
    辅助函数: 调用和风天气 API 获取实时数据
    """
    location_id = REGION_LOCATION_ID.get(region)
    if not location_id:
        return None

    # 检查用户是否忘记填 Key
    if "你的_API_KEY" in QWEATHER_API_KEY:
        print(f"⚠️ [GIS] 未配置 API Key，将使用模拟数据: {region}")
        return None

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                QWEATHER_API_URL,
                params={
                    "location": location_id,
                    "key": QWEATHER_API_KEY,
                    "lang": "zh"
                },
                timeout=5.0  # 设置超时防止卡死
            )
            data = resp.json()

            if data.get("code") == "200":
                now = data["now"]
                # 成功获取！
                return {
                    "temperature": float(now["temp"]),
                    "humidity": float(now["humidity"]),
                    # API 基础版不含海拔，我们混合使用 MOCK 中的海拔数据
                    "altitude": MOCK_GIS_DATA.get(region, {}).get("altitude", 1500.0),
                    "uv_index": MOCK_GIS_DATA.get(region, {}).get("uv_index", 5.0),
                    "sunlight_duration": 7.0
                }
            else:
                print(f"❌ [GIS] 和风 API 错误 (Code {data.get('code')}): {data}")
                return None
    except Exception as e:
        print(f"❌ [GIS] 网络请求异常: {e}")
        return None


@router.get("/environment", response_model=EnvironmentData)
async def get_region_environment(
        region: YunnanRegion = Query(..., description="选择云南的地区，如：昆明、大理")
) -> Any:
    """
    获取指定地区的地理环境数据。
    逻辑：优先调用真实 API -> 失败则使用 Mock 数据 -> 再失败使用默认值
    """
    today_str = datetime.now().strftime("%Y-%m-%d")

    # 1. 尝试调用真实 API
    real_data = await fetch_real_weather(region)

    if real_data:
        return EnvironmentData(
            region=region,
            date=today_str,
            **real_data
        )

    # 2. API 失败，使用 Mock 数据兜底
    data = MOCK_GIS_DATA.get(region)

    # 3. Mock 也没有 (冷门地区)，使用默认值
    if not data:
        data = {
            "altitude": 1500.0, "humidity": 60.0, "temperature": 18.0,
            "uv_index": 5.0, "sunlight_duration": 7.0
        }

    return EnvironmentData(
        region=region,
        date=today_str,
        **data
    )


@router.get("/analysis/stats", response_model=List[EnvironmentData])
async def get_all_regions_stats() -> Any:
    """
    [ECharts 专用接口] 获取所有地区的对比数据
    用于前端绘制 '地区-湿度-海拔' 的双轴图表。
    注意：为了响应速度，这里直接返回模拟数据列表，不循环调用外部 API。
    """
    results = []
    today_str = datetime.now().strftime("%Y-%m-%d")

    for region, data in MOCK_GIS_DATA.items():
        results.append(EnvironmentData(
            region=region,
            date=today_str,
            **data
        ))
    return results