from pydantic_settings import BaseSettings



class Settings(BaseSettings):
    PROJECT_NAME: str = "Yunnan DryEye Knowledge System"
    API_V1_STR: str = "/api/v1"


    # MongoDB 配置
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "dryeye_db"


    # Neo4j 配置
    NEO4J_URI: str = "neo4j+ssc://59660dd2.databases.neo4j.io"
    NEO4J_USER: str = "59660dd2"
    NEO4J_PASSWORD: str = "k5MVWgCeyezZHUkzdG5xK-v8he0AVPV2pzy6kQOfxgA"


    # --- 安全配置 ---
    SECRET_KEY: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # Token 有效期 7 天


    # --- LLM 配置 --
    LLM_API_KEY: str = "sk-b07d03d3c5a84bbc91c888113801ec3b"
    LLM_BASE_URL: str = "https://api.deepseek.com"


class Config:

    case_sensitive = True



settings = Settings() 