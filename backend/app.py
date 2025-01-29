import os
from app import create_app, db
from flask import current_app
import pymysql
from sqlalchemy import text, inspect
from flask_jwt_extended import JWTManager
from datetime import timedelta

def check_db():
    """检查数据库状态"""
    try:
        with current_app.app_context():
            # 测试连接
            db.session.execute(text('SELECT 1'))
            
            # 检查表是否存在
            inspector = inspect(db.engine)
            existing_tables = inspector.get_table_names()
            required_tables = [
                'users', 'companies', 'shareholdings', 'banks', 
                'deposits', 'loans', 'orders', 'trades', 
                'messages', 'message_recipients'
            ]
            
            if not all(table in existing_tables for table in required_tables):
                print("数据库表不完整，开始初始化...")
                return False
            print("数据库连接正常，所有表已存在。")
            return True
    except Exception as e:
        print(f"数据库检查失败：{str(e)}")
        return False

def init_database():
    """初始化数据库"""
    try:
        print("开始初始化数据库...")
        
        # 读取SQL文件
        with open('database/init.sql', 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # 分离触发器和其他SQL
        main_sql = sql_content.split('-- 触发器')[0]
        
        # 连接数据库并执行
        conn = pymysql.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'cs_aiwanba_net'),
            password=os.getenv('DB_PASSWORD', 'sQz9HSnF5ZcXj9SX'),
            charset='utf8mb4'
        )
        
        # 执行主要SQL命令
        with conn.cursor() as cursor:
            for command in main_sql.split(';'):
                if command.strip():
                    cursor.execute(command)
        
        # 创建触发器
        trigger_sql = """
        CREATE TRIGGER after_trade_insert
        AFTER INSERT ON trades
        FOR EACH ROW
        BEGIN
            UPDATE companies 
            SET current_price = NEW.price,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = NEW.company_id;
        END
        """
        try:
            with conn.cursor() as cursor:
                cursor.execute(trigger_sql)
        except Exception as e:
            print(f"触发器创建失败（可能已存在）：{str(e)}")
        
        conn.commit()
        conn.close()
        print("数据库初始化成功！")
        return True
    except Exception as e:
        print(f"数据库初始化失败：{str(e)}")
        return False

app = create_app()

# 确保JWT配置正确
app.config["JWT_SECRET_KEY"] = os.getenv('JWT_SECRET_KEY', 'dev_secret_key')
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)
jwt = JWTManager(app)

@app.cli.command('init-db')
def init_db_command():
    """初始化数据库命令"""
    init_database()

if __name__ == '__main__':
    # 检查数据库状态并按需初始化
    with app.app_context():
        if not check_db() and not init_database():
            print("数据库初始化失败，请检查配置！")
            exit(1)
    
    app.run(host='0.0.0.0', port=5010) 