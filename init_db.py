from app import db, User, Stock, Transaction

def init_database():
    # 删除所有表（谨慎使用，会清空数据）
    db.drop_all()
    
    # 创建所有表
    db.create_all()

    # 添加初始数据（可选）
    # 创建初始用户
    admin_user = User(username='admin', password='admin123')
    db.session.add(admin_user)

    # 创建初始股票
    stocks = [
        Stock(name='科技公司A', symbol='TECH-A', price=100.0),
        Stock(name='能源公司B', symbol='ENER-B', price=50.0),
        Stock(name='医疗公司C', symbol='MEDI-C', price=75.0)
    ]
    db.session.add_all(stocks)

    # 提交更改
    db.session.commit()

    print("数据库初始化完成！")

if __name__ == '__main__':
    init_database() 