from flask import Flask
from extensions import db
from config import config

def init_db():
    """初始化数据库"""
    try:
        app = Flask(__name__)
        app.config.from_object(config['default'])
        
        db.init_app(app)
        
        with app.app_context():
            # 检查数据库连接
            try:
                db.session.execute('SELECT 1')
                print("数据库连接正常")
            except Exception as e:
                print(f"数据库连接错误: {str(e)}")
                return
            
            # 导入所有模型
            from models import User, Company, Stock, StockTransaction, Bank, BankAccount, BankTransaction
            
            # 创建所有表
            db.create_all()
            print("数据库初始化完成！")
            
    except Exception as e:
        print(f"初始化失败: {str(e)}")

if __name__ == '__main__':
    init_db() 