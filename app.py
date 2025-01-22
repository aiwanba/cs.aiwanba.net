from flask import Flask, jsonify
from extensions import app, db
from auth import auth
from trade import trade
from market import simulate_market
from init_db import init_database  # 导入init_database函数
from ai_trader import ai_trade  # 导入ai_trade函数
from leaderboard import get_leaderboard  # 导入get_leaderboard函数
from news import start_news_simulation  # 导入新闻事件模拟函数
import threading
import time

# 配置数据库连接
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://cs_aiwanba_net:sQz9HSnF5ZcXj9SX@localhost:3306/cs_aiwanba_net'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 显式绑定db和app
db.init_app(app)

# 注册auth蓝图
app.register_blueprint(auth, url_prefix='/api/auth')

# 注册trade蓝图
app.register_blueprint(trade, url_prefix='/api/trade')

# 首页路由
@app.route('/')
def index():
    return '欢迎来到股票投资模拟游戏！'

# 排行榜API
@app.route('/api/leaderboard', methods=['GET'])
def leaderboard():
    leaderboard_data = get_leaderboard()
    return jsonify(leaderboard_data)

# 启动股票价格波动模拟
def start_market_simulation():
    while True:
        simulate_market()
        time.sleep(60)  # 每分钟模拟一次价格波动

# 启动AI交易模拟
def start_ai_trading():
    while True:
        ai_trade()
        time.sleep(30)  # 每30秒进行一次AI交易

# 启动新闻事件模拟
def start_news_simulation_thread():
    start_news_simulation()

# 启动应用
if __name__ == '__main__':
    # 初始化数据库
    with app.app_context():
        init_database()

    # 启动股票价格波动模拟线程
    market_thread = threading.Thread(target=start_market_simulation)
    market_thread.daemon = True
    market_thread.start()

    # 启动AI交易模拟线程
    ai_thread = threading.Thread(target=start_ai_trading)
    ai_thread.daemon = True
    ai_thread.start()

    # 启动新闻事件模拟线程
    news_thread = threading.Thread(target=start_news_simulation_thread)
    news_thread.daemon = True
    news_thread.start()

    app.run(host='0.0.0.0', port=5010) 