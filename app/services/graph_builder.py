from neo4j import AsyncGraphDatabase
from app.db.neo4j import neo4j_db
from app.db.mongodb import get_database
import logging

logger = logging.getLogger(__name__)


class GraphBuilderService:
    """
    负责将 MongoDB 中的多模态数据转化为 Neo4j 的图谱结构
    """

    async def build_full_graph(self):
        """
        [核心功能] 从 MongoDB 读取所有数据，重建整个知识图谱
        """
        mongo_db = get_database()

        # 1. 获取所有病人数据
        patients = await mongo_db["patients"].find().to_list(length=1000)
        # 2. 获取所有诊断数据
        diagnoses = await mongo_db["diagnosis"].find().to_list(length=1000)

        # 建立快速查找字典
        diag_map = {str(d["patient_id"]): d for d in diagnoses}

        driver = neo4j_db.driver
        if not driver:
            logger.warning("Neo4j driver is not connected.")
            return {"status": "error", "message": "Neo4j not connected"}

        async with driver.session() as session:
            # A. 清空旧图谱 (慎用，仅用于开发阶段重置)
            await session.run("MATCH (n) DETACH DELETE n")

            # B. 创建基础节点：云南各地区
            regions = [
                "昆明", "大理", "丽江", "西双版纳", "曲靖", "玉溪",
                "红河", "文山", "普洱", "保山", "昭通", "临沧", "楚雄", "德宏", "怒江", "迪庆"
            ]
            for region in regions:
                await session.run(
                    "MERGE (r:Region {name: $name})",
                    name=region
                )

            # C. 创建基础节点：干眼症等级 (Disease)
            levels = ["正常", "轻度", "中度", "重度"]
            for level in levels:
                await session.run(
                    "MERGE (d:Disease {name: $name, type: 'DryEye'})",
                    name=level
                )

            count = 0
            # D. 循环创建病人节点及其关系
            for p in patients:
                p_id = str(p["_id"])
                name = p.get("name", "Unknown")
                region = p.get("location", "昆明")  # 默认昆明

                # 1. 创建病人节点 (Patient)
                await session.run(
                    """
                    CREATE (p:Patient {id: $id, name: $name, age: $age, gender: $gender})
                    """,
                    id=p_id, name=name, age=p.get("age"), gender=p.get("gender")
                )

                # 2. 建立关系: (Patient)-[:LIVES_IN]->(Region)
                await session.run(
                    """
                    MATCH (p:Patient {id: $pid}), (r:Region {name: $region})
                    MERGE (p)-[:LIVES_IN]->(r)
                    """,
                    pid=p_id, region=region
                )

                # 3. 如果有诊断记录，建立关系: (Patient)-[:HAS_DISEASE]->(Disease)
                if p_id in diag_map:
                    diag = diag_map[p_id]
                    # 获取严重程度，假设存储在 ai_analysis.severity 或 doctor_diagnosis
                    severity = "正常"
                    if diag.get("ai_analysis"):
                        severity = diag["ai_analysis"].get("severity", "正常")

                    await session.run(
                        """
                        MATCH (p:Patient {id: $pid}), (d:Disease {name: $sev})
                        MERGE (p)-[:HAS_DISEASE]->(d)
                        """,
                        pid=p_id, sev=severity
                    )
                count += 1

        return {"status": "success", "nodes_created": count}

    async def get_echarts_data(self):
        """
        [ECharts 专用] 获取 D3/ECharts 格式的节点和边
        """
        driver = neo4j_db.driver
        if not driver:
            return {"nodes": [], "links": []}

        async with driver.session() as session:
            # 查询所有节点和关系
            result = await session.run(
                """
                MATCH (n)-[r]->(m)
                RETURN n, r, m LIMIT 300
                """
            )

            nodes = []
            links = []
            node_ids = set()

            async for record in result:
                n = record["n"]
                m = record["m"]
                r = record["r"]

                # 处理源节点
                n_id = n.element_id if hasattr(n, "element_id") else str(n.id)
                if n_id not in node_ids:
                    # 自动判断类别 (根据 Label)
                    label = list(n.labels)[0] if n.labels else "Unknown"
                    # 不同类别给不同颜色/大小 (ECharts category)
                    category = 0
                    if label == "Region":
                        category = 1
                    elif label == "Disease":
                        category = 2

                    nodes.append({
                        "id": n_id,
                        "name": n.get("name", "Unknown"),
                        "category": category,
                        "value": label  # 鼠标悬停显示
                    })
                    node_ids.add(n_id)

                # 处理目标节点
                m_id = m.element_id if hasattr(m, "element_id") else str(m.id)
                if m_id not in node_ids:
                    label = list(m.labels)[0] if m.labels else "Unknown"
                    category = 0
                    if label == "Region":
                        category = 1
                    elif label == "Disease":
                        category = 2

                    nodes.append({
                        "id": m_id,
                        "name": m.get("name", "Unknown"),
                        "category": category,
                        "value": label
                    })
                    node_ids.add(m_id)

                # 处理关系线
                links.append({
                    "source": n_id,
                    "target": m_id,
                    "name": r.type  # 显示在连线上的文字 (如 LIVES_IN)
                })

            return {
                "nodes": nodes,
                "links": links,
                "categories": [
                    {"name": "病人"},
                    {"name": "地区"},
                    {"name": "疾病等级"}
                ]
            }


graph_service = GraphBuilderService()