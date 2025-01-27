from .user import User
from .company import Company
from .stock import Stock, StockTransaction
from .bank import Bank, BankAccount, BankTransaction

def init_db(app):
    """初始化数据库"""
    from extensions import db
    
    with app.app_context():
        # 创建所有表
        db.create_all()
        
        # 检查是否需要创建初始用户
        if not User.query.first():
            # 创建测试用户
            test_user = User(
                username='test',
                email='test@example.com',
                password='123456'
            )
            test_user.balance = 1000000  # 初始资金 100 万
            db.session.add(test_user)
            db.session.commit() 