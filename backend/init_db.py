from flask import Flask
from extensions import db
from config import config

def init_db():
    """初始化数据库"""
    # 创建测试应用
    app = Flask(__name__)
    app.config.from_object(config['default'])
    
    # 初始化数据库
    db.init_app(app)
    
    with app.app_context():
        # 导入所有模型以确保它们被注册
        from models import User, Company, Stock, StockTransaction, Bank, BankAccount, BankTransaction
        
        # 删除所有表
        db.drop_all()
        # 创建所有表
        db.create_all()
        print("数据库初始化完成！")

if __name__ == '__main__':
    init_db() 