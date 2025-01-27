from flask import Flask
from extensions import db
from config import config

def init_db():
    """初始化数据库"""
    app = Flask(__name__)
    app.config.from_object(config['default'])
    
    db.init_app(app)
    
    with app.app_context():
        # 导入所有模型
        from models import User, Company, Stock, StockTransaction, Bank, BankAccount, BankTransaction
        
        # 创建所有表
        db.create_all()
        print("数据库初始化完成！")

if __name__ == '__main__':
    init_db() 