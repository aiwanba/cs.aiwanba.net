from flask import Flask, jsonify, render_template
from datetime import datetime
from models import db
from flask_socketio import SocketIO
from routes.company import company_bp
from routes.trading import trading_bp
from routes.bank import bank_bp
from routes.notification import notification_bp
from routes.market import market_bp

app = Flask(__name__, 
    static_url_path='',
    static_folder='static',
    template_folder='templates'
)

# 数据库配置
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://cs_aiwanba_net:sQz9HSnF5ZcXj9SX@localhost:3306/cs_aiwanba_net'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key'  # 用于WebSocket

db.init_app(app)
socketio = SocketIO(app)

# 确保所有模型都被导入
from models.company import Company
from models.shareholder import Shareholder
from models.transaction import Transaction, OrderBook
from models.bank import BankAccount, TimeDeposit, StockPledgeLoan
from models.notification import Notification

# 创建数据库表
with app.app_context():
    db.create_all()

# 注册蓝图
app.register_blueprint(company_bp)
app.register_blueprint(trading_bp)
app.register_blueprint(bank_bp)
app.register_blueprint(notification_bp)
app.register_blueprint(market_bp)

# 基础路由
@app.route('/')
def index():
    return render_template('index.html')

# WebSocket事件处理
@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    socketio.run(app, port=5010) 