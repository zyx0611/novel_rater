# config.py

# 用于配置连接数据库时的集合名，
# 脚本根据本配置自动判断集合所在的数据库名
DB_GROUPS = {
    "cms": ["articles"],
    "seo_ai": ["content"],
    "pytest": [
        "article_url","result","log",

        # 下面是各站点测试结果result等集合
        "infohivehub.com_result","sportsinfodash.com_result","ovied.com_result","tecnologythis.com_result",
        "bizorfinance.com_result","climatetone.com_result","lawingov.com_result","playersback.com_result",
        "sportsblick.de_result","popfunken.de_result","hugtrends.de_result","khelbeat.in_result"
    ]
}
