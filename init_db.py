from app import app, db
from models.company import Company
from models.shareholder import Shareholder
from models.transaction import Transaction, OrderBook
from models.bank import BankAccount, TimeDeposit, StockPledgeLoan
from models.notification import Notification

def init_database():
    with app.app_context():
        # 创建所有表
        db.create_all()
        print("数据库表创建成功！")

if __name__ == '__main__':
    init_database() 