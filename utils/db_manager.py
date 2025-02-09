"""
数据库连接管理工具
"""
import mysql.connector
from mysql.connector import pooling
from config.db_config import MYSQL_CONFIG
import logging

class DatabaseManager:
    _instance = None
    _pool = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._initialize_pool()
        return cls._instance
    
    def _initialize_pool(self):
        """初始化数据库连接池"""
        try:
            pool_config = MYSQL_CONFIG.copy()
            pool_config.update({
                'pool_name': 'mypool',
                'pool_size': 5,
                'pool_reset_session': True
            })
            self._pool = mysql.connector.pooling.MySQLConnectionPool(**pool_config)
            logging.info("Database connection pool initialized successfully")
        except Exception as e:
            logging.error(f"Error initializing database pool: {str(e)}")
            raise
    
    def get_connection(self):
        """获取数据库连接"""
        try:
            return self._pool.get_connection()
        except Exception as e:
            logging.error(f"Error getting database connection: {str(e)}")
            raise
    
    def execute_query(self, query, params=None):
        """执行查询并返回结果"""
        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            result = cursor.fetchall()
            return result
        except Exception as e:
            logging.error(f"Error executing query: {str(e)}")
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    def execute_update(self, query, params=None):
        """执行更新操作"""
        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            cursor.execute(query, params or ())
            connection.commit()
            return cursor.rowcount
        except Exception as e:
            if connection:
                connection.rollback()
            logging.error(f"Error executing update: {str(e)}")
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close() 