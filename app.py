from backend.app import create_app, db
from backend.app.models import User, Stock, Portfolio
import os

# 创建Flask应用实例
app = create_app()

# 创建数据库表
@app.before_first_request
def create_tables():
    """在第一次请求之前创建所有数据库表"""
    db.create_all()

# 添加命令行命令
@app.cli.command("init-db")
def init_db():
    """初始化数据库"""
    db.create_all()
    print("数据库表已创建。")

@app.cli.command("seed-stocks")
def seed_stocks():
    """添加初始股票数据"""
    stocks = [
        Stock(symbol='AAPL', name='苹果公司', current_price=150.0),
        Stock(symbol='GOOGL', name='谷歌公司', current_price=2800.0),
        Stock(symbol='MSFT', name='微软公司', current_price=300.0),
        Stock(symbol='AMZN', name='亚马逊公司', current_price=3300.0),
        Stock(symbol='TSLA', name='特斯拉公司', current_price=900.0)
    ]
    
    for stock in stocks:
        existing = Stock.query.filter_by(symbol=stock.symbol).first()
        if not existing:
            db.session.add(stock)
    
    db.session.commit()
    print("初始股票数据已添加。")

if __name__ == '__main__':
    # 从环境变量获取配置类型
    config_name = os.environ.get('FLASK_ENV', 'development')
    if config_name == 'production':
        app.config.from_object('config.ProductionConfig')
    else:
        app.config.from_object('config.DevelopmentConfig')
    
    # 根据配置文件中的设置运行应用
    app.run(host='0.0.0.0', port=5010) 