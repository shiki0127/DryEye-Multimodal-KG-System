import httpx
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class LLMService:
    """
    大语言模型服务：负责调用外部 LLM API (如 DeepSeek, ChatGPT)
    """

    def __init__(self):
        self.api_key = settings.LLM_API_KEY
        self.base_url = settings.LLM_BASE_URL

    async def chat_completion(self, message: str, context: str = ""):
        """
        发送对话请求
        :param message: 用户当前的问题
        :param context: 上下文信息 (比如病人的诊断记录)
        """
        if "sk-" not in self.api_key:
            return "⚠️ AI 服务未配置 API Key，无法回答。"

        system_prompt = """
        你是一个专业的眼科辅助诊疗 AI 助手。
        请基于提供的病人诊断数据和医学知识，为医生提供分析建议。
        回答要专业、简洁，并提醒这只是辅助建议，不是最终确诊。
        """

        full_prompt = f"上下文信息：{context}\n\n用户问题：{message}"

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # 这是一个通用的 OpenAI 格式接口调用
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "deepseek-chat",  # 或 gpt-3.5-turbo
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": full_prompt}
                        ],
                        "temperature": 0.7
                    }
                )

                if response.status_code != 200:
                    logger.error(f"LLM API Error: {response.text}")
                    return "AI 服务暂时不可用，请稍后再试。"

                result = response.json()
                return result["choices"][0]["message"]["content"]

        except Exception as e:
            logger.error(f"LLM Request Failed: {e}")
            return "网络连接异常，无法连接到 AI 模型。"


llm_service = LLMService()