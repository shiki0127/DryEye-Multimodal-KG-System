from fastapi import APIRouter

router = APIRouter()

@router.get("/weather")
async def get_regional_environment(lat: float, lon: float):
    # TODO: 请求外部 GIS/天气 API
    # 模拟返回高原环境数据
    return {
        "location": {"lat": lat, "lon": lon},
        "altitude": 3200, # 海拔 3200m
        "uv_index": 9,    # 强紫外线
        "humidity": 30    # 干燥
    }