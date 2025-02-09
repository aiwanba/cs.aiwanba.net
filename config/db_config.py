"""
数据库配置文件
"""
import os
from dotenv import load_dotenv

load_dotenv()

MYSQL_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'cs_aiwanba_net'),
    'password': os.getenv('DB_PASSWORD', 'sQz9HSnF5ZcXj9SX'),
    'database': os.getenv('DB_NAME', 'cs_aiwanba_net'),
    'port': int(os.getenv('DB_PORT', 3306))
} 