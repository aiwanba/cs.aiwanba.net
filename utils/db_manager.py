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
    
    def fetch_all(self, query, params=None):
        """执行查询并返回所有结果"""
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
            return []
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    def execute_query(self, query, params=None):
        """执行更新操作"""
        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            cursor.execute(query, params or ())
            connection.commit()
            return True
        except Exception as e:
            if connection:
                connection.rollback()
            logging.error(f"Error executing update: {str(e)}")
            return False
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

    def save_message(self, session_id, role, content):
        """保存聊天消息"""
        try:
            sql = """
                INSERT INTO chat_history (session_id, role, content)
                VALUES (%s, %s, %s)
            """
            self.execute_query(sql, (session_id, role, content))
            return True
        except Exception as e:
            logging.error(f"Error saving message: {str(e)}")
            return False

    def get_session_messages(self, session_id):
        """获取会话的所有消息"""
        try:
            sql = """
                SELECT role, content, created_at
                FROM chat_history
                WHERE session_id = %s
                ORDER BY id ASC
            """
            return self.fetch_all(sql, (session_id,))
        except Exception as e:
            logging.error(f"Error getting session messages: {str(e)}")
            return []

    def create_session(self, session_id, title):
        """创建新会话"""
        try:
            sql = """
                INSERT INTO chat_sessions (session_id, title)
                VALUES (%s, %s)
            """
            self.execute_query(sql, (session_id, title))
            return True
        except Exception as e:
            logging.error(f"Error creating session: {str(e)}")
            return False

    def get_all_sessions(self):
        """获取所有会话"""
        try:
            sql = """
                SELECT session_id, title, created_at, updated_at
                FROM chat_sessions
                ORDER BY updated_at DESC
            """
            return self.fetch_all(sql)
        except Exception as e:
            logging.error(f"Error getting sessions: {str(e)}")
            return []

    def delete_session(self, session_id):
        """删除会话及其消息"""
        try:
            # 删除消息
            sql1 = "DELETE FROM chat_history WHERE session_id = %s"
            self.execute_query(sql1, (session_id,))
            
            # 删除会话
            sql2 = "DELETE FROM chat_sessions WHERE session_id = %s"
            self.execute_query(sql2, (session_id,))
            return True
        except Exception as e:
            logging.error(f"Error deleting session: {str(e)}")
            return False 