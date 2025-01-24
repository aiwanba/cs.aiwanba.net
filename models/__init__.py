from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_models(app):
    """初始化所有模型"""
    db.init_app(app)
    
    # 导入所有模型
    from .user import User
    from .company import Company
    from .stock import Stock
    from .bank import BankAccount, BankTransaction
    from .transaction import Transaction, Order
    from .ai_strategy import AIStrategy, AITrader
    
    return db 