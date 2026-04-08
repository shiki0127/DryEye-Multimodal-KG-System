from fastapi import APIRouter

router = APIRouter()

@router.post("/ask")
async def ask_ai_doctor(query: dict):
    user_message = query.get("message", "")
    # TODO: 1. 从 Neo4j 检索相关实体 (RAG)
    # TODO: 2. 拼接 Prompt 调用 DeepSeek API
    # TODO: 3. 队友负责的 DeepSeek 接口对接逻辑放这里
    mock_response = f"根据您的主诉'{user_message}'以及高原环境特征，建议您注意防范紫外线引发的眼表疾病。"
    return {"reply": mock_response, "source_nodes": ["强紫外线", "翼状胬肉"]}