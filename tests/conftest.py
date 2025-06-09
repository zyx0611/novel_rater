import os
from scorer.allure_parser import AllureResultParser
from scorer.db_operator import insert_many, insert_one
from scorer.log import logger

# 定义路径
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
LOG_FILE_PATH = os.path.join(BASE_DIR, 'tests', 'run_logs', 'pytest.log')
ERROR_FILE_PATH = os.path.join(BASE_DIR, 'tests', 'run_logs', 'error_url.csv')

def get_allure_results_dir(domain_name: str):
    """
    根据 domain_name 构造 Allure 结果目录路径
    """
    safe_domain = domain_name.replace('.', '_')
    return os.path.join(BASE_DIR, f"tests/allure-results/{safe_domain}")

def pytest_unconfigure(config):
    """
    pytest 执行完所有 teardown、Allure 插件完成写入后，才执行此钩子
    """
    logger.info("pytest 退出前，执行 Allure 结果解析...")

    # allure_results_dir = get_allure_results_dir(domain_name)
    allure_results_dir = os.path.join(BASE_DIR, f"allure-results")
    parser = AllureResultParser(allure_results_dir)
    records = parser.parse_all_files()
    if records:
        insert_many('text_result', records)
        logger.info(f"成功写入 {len(records)} 条测试记录到 MongoDB 集合 text_result")
    else:
        logger.warning("没有解析到有效的 Allure 测试记录，跳过数据库写入。")

    if os.path.exists(LOG_FILE_PATH):
        with open(LOG_FILE_PATH, "r", encoding="utf-8") as f:
            log_content = f.read()

        if log_content.strip():
            log_record = {
                "log": log_content,
                "project": "AI-SEO",
                "env": "test",  # 可根据需要切换
                "filename": "pytest.log"
            }
            insert_one('log', log_record)
            logger.info("成功保存日志到 MongoDB 集合 log")
        else:
            logger.warning("pytest.log 文件为空，跳过日志写入。")
    else:
        logger.warning("pytest.log 文件不存在，无法保存日志。")
