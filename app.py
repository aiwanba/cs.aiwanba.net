from extensions import app, db
from auth import auth
from trade import trade
from market import simulate_market
from init_db import init_database  # 导入init_database函数
import threading
import time

# 配置数据库连接
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://cs_aiwanba_net:sQz9HSnF5ZcXj9SX@localhost:3306/cs_aiwanba_net'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 注册auth蓝图
app.register_blueprint(auth, url_prefix='/api/auth')

# 注册trade蓝图
app.register_blueprint(trade, url_prefix='/api/trade')

# 首页路由
@app.route('/')
def index():
    return '欢迎来到股票投资模拟游戏！'

# 启动股票价格波动模拟
def start_market_simulation():
    while True:
        simulate_market()
        time.sleep(60)  # 每分钟模拟一次价格波动

# 启动应用
if __name__ == '__main__':
    # 初始化数据库
    with app.app_context():
        init_database()

    # 启动股票价格波动模拟线程
    market_thread = threading.Thread(target=start_market_simulation)
    market_thread.daemon = True
    market_thread.start()

    app.run(host='0.0.0.0', port=5010) 