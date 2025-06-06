# utils/log.py
import logging
import os

# 日志输出目录（默认放在 tests/run_logs/ 目录下）
log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tests', 'run_logs')
os.makedirs(log_dir, exist_ok=True)

# 日志文件路径
log_file = os.path.join(log_dir, 'pytest.log')

# 创建 Logger 实例
logger = logging.getLogger("pytest_logger")
logger.setLevel(logging.INFO)

# 日志输出格式
formatter = logging.Formatter(
    fmt="%(levelname)-8s %(asctime)s [%(filename)s:%(lineno)d] - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# 输出到文件的Handler
file_handler = logging.FileHandler(log_file, encoding="utf-8")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# 输出到控制台的Handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# 暴露log_file以供其他模块使用
__all__ = ["logger", "log_file"]
