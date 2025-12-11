from neo4j import GraphDatabase
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class Neo4jDB:
    def __init__(self):
        self.driver = None

    def connect(self):
        """初始化 Neo4j 连接"""
        logger.info("Connecting to Neo4j...")
        try:
            # 使用 GraphDatabase.driver 建立连接
            self.driver = GraphDatabase.driver(
                settings.NEO4J_URI,
                auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
            )
            # 验证连接
            self.driver.verify_connectivity()
            logger.info("✅ Neo4j connected successfully!")
        except Exception as e:
            logger.error(f"❌ Neo4j connection failed: {e}")
            raise e

    def close(self):
        """关闭连接"""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j connection closed.")

    def get_session(self):
        """获取一个新的会话"""
        if not self.driver:
            raise ConnectionError("Neo4j driver not initialized")
        return self.driver.session()

neo4j_db = Neo4jDB()

def get_neo4j_session():
    """依赖注入函数：获取 Neo4j Session"""
    session = neo4j_db.get_session()
    try:
        yield session
    finally:
        session.close()