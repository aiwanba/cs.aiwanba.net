from .user import User
from .company import Company
from .stock import Stock, StockTransaction
from .bank import Bank, BankAccount, BankTransaction
from .order import Order

def init_db(app):
    """初始化数据库"""
    from extensions import db
    
    with app.app_context():
        # 创建所有表
        db.create_all() 