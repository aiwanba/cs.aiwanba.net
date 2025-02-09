"""
数据库初始化脚本
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.db_manager import DatabaseManager

def init_database():
    """初始化数据库表"""
    db = DatabaseManager()
    
    # 读取SQL文件
    with open('sql/chat_history.sql', 'r', encoding='utf-8') as f:
        sql_commands = f.read().split(';')
    
    # 执行每个SQL命令
    for command in sql_commands:
        if command.strip():
            try:
                db.execute_query(command)
                print(f"Executed SQL: {command[:50]}...")
            except Exception as e:
                print(f"Error executing SQL: {str(e)}")
                continue

if __name__ == "__main__":
    print("Initializing database...")
    init_database()
    print("Database initialization completed.") 