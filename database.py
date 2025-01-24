import pymysql

def get_db_connection():
    """数据库连接配置"""
    return pymysql.connect(
        host='localhost',
        user='cs_aiwanba_net',
        password='sQz9HSnF5ZcXj9SX',
        database='cs_aiwanba_net',
        port=3306,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    ) 