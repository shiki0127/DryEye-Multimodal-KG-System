from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class MongoDB:
    client: AsyncIOMotorClient = None
    db_name: str = settings.MONGODB_DB_NAME

db = MongoDB()

async def connect_to_mongo():
    """初始化 MongoDB 连接"""
    logger.info("Connecting to MongoDB...")
    try:
        db.client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            maxPoolSize=10,
            minPoolSize=10
        )
        # 尝试执行一个简单的命令来验证连接
        await db.client.server_info()
        logger.info("✅ MongoDB connected successfully！")
    except Exception as e:
        logger.error(f"❌ MongoDB connection failed: {e}")
        raise e

async def close_mongo_connection():
    """关闭 MongoDB 连接"""
    logger.info("Closing MongoDB connection...")
    if db.client:
        db.client.close()
        logger.info("MongoDB connection closed.")

def get_database():
    """依赖注入函数：获取数据库实例"""
    return db.client[db.db_name]