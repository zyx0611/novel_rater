# utils/allure_parser.py
import ast
import os
import json
import time
import chardet
import traceback
from scorer import db_operator
from scorer.log import logger

class AllureResultParser:
    """
    解析 Allure pytest 生成的 JSON 测试结果，并保存到 MongoDB
    """

    def __init__(self, allure_results_dir: str, collection_name: str = "result"): # 修改默认值
        if not allure_results_dir:
            raise ValueError("必须提供 allure_results_dir")
        self.allure_results_dir = allure_results_dir
        self.collection_name = collection_name
        self.run_id = int(time.time() * 1000)
        logger.info(f"AllureResultParser 初始化，run_id = {self.run_id}，解析目录：{self.allure_results_dir}，目标集合：{self.collection_name}")

    def parse_all_files(self) -> list:

        all_records = []
        files = os.listdir(self.allure_results_dir)
        logger.info(f"{self.allure_results_dir}目录下共找到 {len(files)} 个文件")

        # logger.info("扫描到的 JSON 文件列表：")
        # for f in files:
        #     logger.info(f"- {f}")

        for filename in files:
            if not filename.endswith("-result.json"):
                continue

            file_path = os.path.join(self.allure_results_dir, filename)
            logger.info(f"准备解析文件: {filename}")
            try:
                with open(file_path, "rb") as f:
                    raw_data = f.read()

                encoding = chardet.detect(raw_data).get("encoding", "utf-8")
                text = raw_data.decode(encoding)
                data = json.loads(text)

                records = self.extract_records(data)
                logger.info(f"文件 {filename} 解析出 {len(records)} 条记录")
                all_records.extend(records)
            except Exception as e:
                logger.error(f"解析文件失败: {file_path}, 错误: {e}")
                traceback.print_exc()

        logger.info(f"成功解析出 {len(all_records)} 条测试记录")
        return all_records

    def extract_records(self, data: dict) -> list:
        records = []

        def parse_step(step, parent_name=""):
            if not step.get('status'):
                return None

            return {
                'date': step.get('parameters', []) and step['parameters'][0].get('value'),
                'url': step.get('links', []) and step['links'][0].get('url'),
                'run_id': self.run_id,
                'links': step.get('links', []),
                'name': step.get('name', ''),
                'fullName': parent_name + "::" + step.get('name', '') if parent_name else step.get('name', ''),
                'status': step.get('status', ''),
                # 'statusDetails': step.get('statusDetails', []),
                'statusDetails': step.get('statusDetails', {}).get('message', {}),
                'start': step.get('start', 0),
                'stop': step.get('stop', 0),
                'duration': step.get('stop', 0) - step.get('start', 0),
                'parameters': step.get('parameters', []),
                'steps': step.get('steps', []),
                'attachments': step.get('attachments', []),
                'description': step.get('description', ''),
                'labels': data.get('labels', [])
            }

        if data.get("status"):
            logger.info(f"解析主测试记录: {data.get('name')} ({data.get('status')})")
            novel_result = data.get('attachments', [{'info': '评分结果为空!'}])[0]
            novel_info = {}
            if novel_result.get('source') is not None and novel_result.get('name') == '文章评分返回结果':
                with open(f"allure-results/{novel_result.get('source')}", 'r') as f:
                    text = f.read()
                    novel_info = text
            records.append({
                'run_id': self.run_id,
                'name': data.get('name', ''),
                'fullName': data.get('fullName', ''),
                'status': data.get('status', ''),
                # 'statusDetails': data.get('statusDetails', []),
                'start': data.get('start', 0),
                'stop': data.get('stop', 0),
                'duration': data.get('stop', 0) - data.get('start', 0),
                'labels': data.get('labels', []),
                'novel_result': novel_info
            })
        else:
            logger.warning("主测试数据缺少 status 字段，跳过")

        for step in data.get('steps', []):
            rec = parse_step(step, parent_name=data.get('fullName', ''))
            if rec:
                records.append(rec)

        return records

    def save_records(self, records: list):
        if not records:
            logger.warning("没有需要保存的测试记录，跳过写入数据库")
            return

        logger.info(f"即将写入 MongoDB 的记录数: {len(records)}")
        for i, r in enumerate(records):
            logger.info(f"[记录 {i+1}] name={r.get('name')}, status={r.get('status')}, fullName={r.get('fullName')}")

        inserted_ids = db_operator.insert_many(self.collection_name, records)
        logger.info(f"成功保存 {len(inserted_ids)} 条记录到 MongoDB 集合：{self.collection_name}")

    def run(self):
        logger.info("开始解析 Allure 测试结果...")
        records = self.parse_all_files()
        self.save_records(records)
        logger.info("Allure 结果解析任务完成")
