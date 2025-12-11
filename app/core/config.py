from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Yunnan DryEye Knowledge System"
    API_V1_STR: str = "/api/v1"

    # 数据库配置 (暂时使用默认值，后续改为从 .env 读取)
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "dryeye_db"

    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "password"

    class Config:
        case_sensitive = True


settings = Settings()