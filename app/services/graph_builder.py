from app.db.mongodb import get_database
from app.db.neo4j import neo4j_db
import logging

logger = logging.getLogger(__name__)


class GraphBuilderService:
    """
    负责将 MongoDB 中的多模态数据（病人基础信息 + 临床问卷 + 诊断结果）
    转化为 Neo4j 的知识图谱结构
    """

    async def build_full_graph(self):
        """
        [核心功能] 从 MongoDB 读取所有数据，重建整个知识图谱
        """
        # =================================================================
        # 1. 从 MongoDB 获取数据 (使用 get_database 函数)
        # =================================================================

        # 获取数据库实例
        mongo_db = get_database()

        # 再次检查一下拿到没有
        if mongo_db is None:
            logger.error("无法获取 MongoDB 连接，请检查 app/db/mongodb.py")
            return {"status": "error", "message": "MongoDB 未连接"}

        # 获取基础病人信息
        patients = await mongo_db["patients"].find().to_list(length=1000)

        # 获取临床详细病历
        clinical_records = await mongo_db["clinical_records"].find().to_list(length=1000)

        # 建立查找字典：用 patient_id 快速找到对应的病历
        record_map = {str(r["patient_id"]): r for r in clinical_records if "patient_id" in r}

        driver = neo4j_db.driver
        if not driver:
            logger.warning("Neo4j driver is not connected.")
            return {"status": "error", "message": "Neo4j not connected"}

        # =================================================================
        # 2. 写入 Neo4j (使用同步 Session)
        # =================================================================
        with driver.session() as session:
            # A. 清空旧图谱 (开发阶段方便重置)
            session.run("MATCH (n) DETACH DELETE n")

            # B. 预埋基础节点

            # 地区
            regions = [
                "昆明", "大理", "丽江", "西双版纳", "曲靖", "玉溪",
                "红河", "文山", "普洱", "保山", "昭通", "临沧", "楚雄", "德宏", "怒江", "迪庆"
            ]
            for region in regions:
                session.run("MERGE (r:Region {name: $name})", name=region)

            # 全身疾病
            systemic_diseases = ["高血压", "糖尿病", "心脏病", "肾病", "风湿免疫病", "甲状腺疾病", "面神经麻痹"]
            for disease in systemic_diseases:
                session.run("MERGE (d:SystemicDisease {name: $name})", name=disease)

            # 药物
            medicines = ["降压药", "降脂药", "降糖药", "激素类", "免疫抑制剂", "安眠药"]
            for med in medicines:
                session.run("MERGE (m:Medicine {name: $name})", name=med)

            # 生活习惯
            habits = ["吸烟", "饮酒", "高频电子屏使用", "缺乏户外活动"]
            for habit in habits:
                session.run("MERGE (h:Lifestyle {name: $name})", name=habit)

            count = 0

            # C. 循环构建病人及其关系
            for p in patients:
                p_id = str(p["_id"])
                name = p.get("name", "未知患者")
                region = p.get("region", "昆明")

                # 1. 创建病人节点 (Patient) & 居住关系
                session.run(
                    """
                    MERGE (p:Patient {id: $id})
                    SET p.name = $name, p.age = $age, p.gender = $gender
                    WITH p
                    MATCH (r:Region {name: $region})
                    MERGE (p)-[:LIVES_IN]->(r)
                    """,
                    id=p_id, name=name, age=p.get("age"), gender=p.get("gender"), region=region
                )

                # 2. 关联临床病历数据
                if p_id in record_map:
                    record = record_map[p_id]

                    # --- 2.1 全身病史关联 ---
                    sys_hist = record.get("systemic_history", {})
                    disease_mapping = {
                        "has_hypertension": "高血压",
                        "has_diabetes": "糖尿病",
                        "has_heart_disease": "心脏病",
                        "has_kidney_disease": "肾病",
                        "has_rheumatic": "风湿免疫病",
                        "has_thyroid": "甲状腺疾病",
                        "has_facial_paralysis": "面神经麻痹"
                    }

                    for field, disease_name in disease_mapping.items():
                        if sys_hist.get(field) is True:
                            session.run(
                                """
                                MATCH (p:Patient {id: $pid})
                                MATCH (d:SystemicDisease {name: $dname})
                                MERGE (p)-[:HAS_HISTORY]->(d)
                                """,
                                pid=p_id, dname=disease_name
                            )

                    # --- 2.2 用药史关联 ---
                    med_hist = record.get("medication_history", {})
                    med_mapping = {
                        "use_antihypertensive": "降压药",
                        "use_lipid_lowering": "降脂药",
                        "use_hypoglycemic": "降糖药",
                        "use_hormone": "激素类",
                        "use_immunosuppressant": "免疫抑制剂",
                        "use_sleeping_pills": "安眠药"
                    }

                    for field, med_name in med_mapping.items():
                        if med_hist.get(field) is True:
                            session.run(
                                """
                                MATCH (p:Patient {id: $pid})
                                MATCH (m:Medicine {name: $mname})
                                MERGE (p)-[:TAKES_MEDICATION]->(m)
                                """,
                                pid=p_id, mname=med_name
                            )

                    # --- 2.3 生活习惯推断 ---
                    lifestyle = record.get("lifestyle", {})

                    # 规则: 吸烟
                    if lifestyle.get("smoking_history") == "是":
                        session.run(
                            "MATCH (p:Patient {id: $pid}), (h:Lifestyle {name: '吸烟'}) MERGE (p)-[:HAS_HABIT]->(h)",
                            pid=p_id)

                    # 规则: 电子屏幕时间 > 8小时
                    screen_hours = lifestyle.get("daily_screen_hours", 0)
                    if isinstance(screen_hours, (int, float)) and screen_hours > 8:
                        session.run(
                            "MATCH (p:Patient {id: $pid}), (h:Lifestyle {name: '高频电子屏使用'}) MERGE (p)-[:HAS_HABIT]->(h)",
                            pid=p_id)

                count += 1

        return {"status": "success", "nodes_processed": count}

    async def get_echarts_data(self):
        """
        [ECharts 专用] 获取 D3/ECharts 格式的节点和边
        """
        driver = neo4j_db.driver
        if not driver:
            return {"nodes": [], "links": []}

        with driver.session() as session:
            result = session.run(
                """
                MATCH (n)-[r]->(m)
                RETURN n, r, m LIMIT 300
                """
            )

            nodes = []
            links = []
            node_ids = set()

            category_map = {
                "Patient": 1,
                "Region": 2,
                "SystemicDisease": 3,
                "Medicine": 4,
                "Lifestyle": 5
            }

            for record in result:
                n = record["n"]
                m = record["m"]
                r = record["r"]

                def process_node(node):
                    n_id = node.element_id if hasattr(node, "element_id") else str(node.id)
                    if n_id not in node_ids:
                        label = list(node.labels)[0] if node.labels else "Unknown"
                        cat = category_map.get(label, 0)
                        nodes.append({
                            "id": n_id,
                            "name": node.get("name", "未知"),
                            "category": cat,
                            "value": label
                        })
                        node_ids.add(n_id)
                    return n_id

                source_id = process_node(n)
                target_id = process_node(m)

                links.append({
                    "source": source_id,
                    "target": target_id,
                    "name": type(r).__name__
                })

            return {
                "nodes": nodes,
                "links": links,
                "categories": [
                    {"name": "其他"},
                    {"name": "病人"},
                    {"name": "地区"},
                    {"name": "全身疾病"},
                    {"name": "药物"},
                    {"name": "生活习惯"}
                ]
            }


graph_service = GraphBuilderService()