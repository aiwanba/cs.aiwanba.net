# 导入必要的库
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import os
import pymysql

# 创建Flask应用实例
app = Flask(__name__)

# 配置数据库连接
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://cs_aiwanba_net:sQz9HSnF5ZcXj9SX@localhost:3306/cs_aiwanba_net'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(24)

# 创建数据库实例
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# 导入模型（必须在创建db之后导入）
from models.user import User
from models.company import Company
from models.stock import Stock
from models.bank import BankAccount, BankTransaction
from models.transaction import Transaction, Order
from models.ai_strategy import AIStrategy, AITrader

# 导入蓝图和定时任务
from api.bank_api import bank_bp
from api.transaction_api import transaction_bp
from api.stock_api import stock_bp
from api.ai_trading_api import ai_trading_bp
from tasks.stock_price_updater import setup_stock_price_updater

# 注册蓝图
app.register_blueprint(bank_bp, url_prefix='/api/bank')
app.register_blueprint(transaction_bp, url_prefix='/api/transaction')
app.register_blueprint(stock_bp, url_prefix='/api/stock')
app.register_blueprint(ai_trading_bp, url_prefix='/api/ai-trading')

# 启动定时任务
setup_stock_price_updater()

# 创建基本路由
@app.route('/')
def index():
    return jsonify({
        "status": "success",
        "message": "股票交易游戏API服务正在运行"
    })

# 在导入部分添加
pymysql.install_as_MySQLdb()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5010, debug=True) 