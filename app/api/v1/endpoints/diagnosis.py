from fastapi import APIRouter, UploadFile, File

router = APIRouter()

@router.post("/upload")
async def upload_fundus_image(patient_id: str, file: UploadFile = File(...)):
    # TODO: 1. 将图片保存到本地 / 未来接入 MinIO
    # TODO: 2. 调用队友封装好的 U-KAN 和 EyePCR (CBAM) 模型进行推理
    # TODO: 3. 将视觉识别出的病灶特征 (如: 微血管瘤) 存入图谱
    return {
        "filename": file.filename,
        "segmentation_mask": "/static/masks/mock_mask.png",
        "classification_result": "糖尿病视网膜病变 I期",
        "confidence": 0.92
    }