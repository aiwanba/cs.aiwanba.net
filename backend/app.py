import os
from app import create_app, db
from flask import current_app
import pymysql

def init_database():
    """初始化数据库"""
    try:
        # 读取SQL文件
        with open('database/init.sql', 'r', encoding='utf-8') as f:
            sql_commands = f.read()
        
        # 连接数据库
        conn = pymysql.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'cs_aiwanba_net'),
            password=os.getenv('DB_PASSWORD', 'sQz9HSnF5ZcXj9SX'),
            charset='utf8mb4'
        )
        
        # 执行SQL命令
        with conn.cursor() as cursor:
            for command in sql_commands.split(';'):
                if command.strip():
                    cursor.execute(command)
        conn.commit()
        conn.close()
        print("数据库初始化成功！")
        return True
    except Exception as e:
        print(f"数据库初始化失败：{str(e)}")
        return False

app = create_app(os.getenv('FLASK_CONFIG', 'default'))

# 添加命令行指令
@app.cli.command('init-db')
def init_db_command():
    """初始化数据库命令"""
    init_database()

if __name__ == '__main__':
    # 如果环境变量INIT_DB=1，则初始化数据库
    if os.getenv('INIT_DB') == '1':
        init_database()
    app.run(host='0.0.0.0', port=5010) 