# db_operator.py
from pymongo import MongoClient
from contextlib import contextmanager
from dotenv import load_dotenv
from scorer.log import logger

# ========== 全局连接池缓存 ==========
GLOBAL_CLIENTS = {}  # {database_name: MongoClient实例}

# ==========数据连接工具函数============


# ========== 加载环境配置 ==========

def load_mongo_config(collection_name=None):
    """
    加载指定身份的 MongoDB 连接配置。
    Args:
        identity (str, optional): 身份标识符。如果为 None，则加载默认配置。
                                    例如: 'user1', 'user2', 'admin'。默认为 None。
    Returns:
        dict: 包含 MongoDB 连接配置的字典，或者在配置缺失时返回 None。
    """
    load_dotenv()  # 确保加载 .env 文件

    # 从环境变量中读取MongoDB连接参数
    # mongo_host = os.getenv('MONGO_HOST', '127.0.0.1')
    # mongo_port_str = os.getenv('MONGO_PORT', '27017')
    # mongo_port = int(mongo_port_str) if mongo_port_str.isdigit() else 27017
    # mongo_user = os.getenv('MONGO_USER', 'seo_ai')
    # mongo_pass = os.getenv('MONGO_PASS', '14f118d5f470da591218e9a5')
    mongo_host = 'mongo'
    mongo_port = '27017'
    mongo_user = 'root'
    mongo_pass = 'example'

    mongo_db_name = 'seo_ai'

    if mongo_host and mongo_user and mongo_pass and mongo_db_name:
        return {
            'host': mongo_host,
            'port': mongo_port,
            'user': mongo_user,
            'password': mongo_pass,
            'database': mongo_db_name
        }
    else:
        logger.info(f"警告: 无法加载完整 MongoDB 配置。请检查 .env 文件。")
        return None


# ========== MongoDB连接管理器 ==========

@contextmanager
def get_connection(collection_name):
    """
    上下文管理器：获取 MongoDB 数据库连接（使用全局连接池缓存）。
    - 第一次连接指定库时创建 MongoClient 实例并缓存，后续复用。
    - 返回 db 对象供使用，不会每次都关闭连接。
    """
    config = load_mongo_config(collection_name)
    if not config:
        raise RuntimeError(f"❌ 无法加载集合 `{collection_name}` 的 MongoDB 配置，连接中止。")

    db_name = config['database']

    if db_name not in GLOBAL_CLIENTS:
        uri = f"mongodb://{config['user']}:{config['password']}@{config['host']}:{config['port']}/?authSource=admin"
        client = MongoClient(
            uri,
            maxPoolSize=50,
            serverSelectionTimeoutMS=5000,
            socketTimeoutMS=30000,
        )
        GLOBAL_CLIENTS[db_name] = client
        logger.info(f"MongoClient 初始化完成：{db_name}")
    else:
        client = GLOBAL_CLIENTS[db_name]

    db = client[db_name]

    try:
        yield db  # 返回数据库连接
    finally:
        # 不再关闭连接，复用连接池
        pass

# ========== 封装常用数据库操作方法 ==========
def aggregate(collection_name: str, pipeline: list):
    """
    聚合查询
    :param collection_name: 集合名
    :param pipeline: 聚合管道（list）
    :return: 聚合结果（列表）
    """
    with get_connection(collection_name) as db:
        collection = db[collection_name]
        return list(collection.aggregate(pipeline))

def insert_one(collection_name: str, data: dict):
    """
    向指定集合插入单条文档
    :param collection_name: 集合名
    :param data: 需要插入的字典数据
    :return: 新插入文档的ID
    """
    with get_connection(collection_name) as db:
        collection = db[collection_name]
        result = collection.insert_one(data)
        return result.inserted_id

def insert_many(collection_name: str, data_list: list):
    """
    向指定集合批量插入多条文档
    :param collection_name: 集合名
    :param data_list: 包含多个字典的列表
    :return: 插入后每条文档的ID列表
    """
    logger.info(f"[DEBUG] insert into MongoDB collection: {collection_name}")
    with get_connection(collection_name) as db:
        collection = db[collection_name]
        try:
            result = collection.insert_many(data_list,ordered=False)
            return [doc_id for doc_id in result.inserted_ids]
        except Exception as e:
            logger.info(f"批量插入MongoDB失败：{e}")
            return []


def find_one(collection_name: str, query: dict):
    """
    查询符合条件的第一条文档
    :param collection_name: 集合名
    :param query: 查询条件
    :return: 查询到的文档（字典）
    """
    with get_connection(collection_name) as db:
        collection = db[collection_name]
        return collection.find_one(query)

def find_one_sorted(collection_name: str, query: dict, sort_field: str, descending=True):
    """
    查询符合条件的第一条文档，并按字段排序
    :param collection_name: 集合名
    :param query: 查询条件
    :param sort_field: 排序字段名
    :param descending: 是否降序（默认为True）
    :return: 查询到的文档（字典）
    """
    from pymongo import DESCENDING, ASCENDING
    sort_order = DESCENDING if descending else ASCENDING

    with get_connection(collection_name) as db:
        collection = db[collection_name]
        return collection.find_one(query, sort=[(sort_field, sort_order)])

def find_many_sorted(collection_name: str, query: dict, sort_field: str, descending=True):
    """
    查询符合条件的所有文档，并按字段排序
    :param collection_name: 集合名
    :param query: 查询条件
    :param sort_field: 排序字段名
    :param descending: 是否降序（默认为True）
    :return: 查询到的文档（字典）
    """
    from pymongo import DESCENDING, ASCENDING
    sort_order = DESCENDING if descending else ASCENDING

    with get_connection(collection_name) as db:
        collection = db[collection_name]
        return list(collection.find(query, sort=[(sort_field, sort_order)]))

def find_many(collection_name: str, query: dict):
    """
    查询符合条件的所有文档
    :param collection_name: 集合名
    :param query: 查询条件
    :return: 查询到的文档列表
    """
    with get_connection(collection_name) as db:
        collection = db[collection_name]
        return list(collection.find(query))

def show_collection(collection_name: str):
    """
    打印指定集合中的所有文档
    :param collection_name: 集合名
    """
    # config = load_mongo_config(collection_name)
    with get_connection(collection_name) as db:
        collection = db[collection_name]

        # 打印每条数据
        # for document in collection.find({}):
        #     logger.info(document)

        # 打印数据记录条数
        logger.info(collection.count_documents({}))


def update_one(collection_name: str, query: dict, update_data: dict):
    """
    更新符合条件的一条文档
    :param collection_name: 集合名
    :param query: 查询条件
    :param update_data: 需要更新的数据（只支持$set更新）
    :return: 修改的文档数量（0或1）
    """
    with get_connection(collection_name) as db:
        collection = db[collection_name]
        result = collection.update_one(query, {"$set": update_data})
        return result.modified_count


def delete_one(collection_name: str, query: dict):
    """
    删除符合条件的一条文档
    :param collection_name: 集合名
    :param query: 删除条件
    :return: 删除的文档数量（0或1）
    """
    with get_connection(collection_name) as db:
        collection = db[collection_name]
        result = collection.delete_one(query)
        return result.deleted_count


def drop_collection(collection_name: str):
    """
    删除整个集合（危险操作，谨慎调用）
    :param collection_name: 集合名
    """
    with get_connection(collection_name) as db:
        db.drop_collection(collection_name)
        logger.info(f"集合 {collection_name} 已被删除")

# 关闭全局连接池
def close_all_connections():
    for db_name, client in GLOBAL_CLIENTS.items():
        client.close()
        logger.info(f"已关闭 MongoDB 连接：{db_name}")
