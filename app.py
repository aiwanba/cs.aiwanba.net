from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from apps.models import user, company, stock, transaction, bank, news, ai
from apps.api.bank import bank_bp
from apps.api.news import news_bp
from apps.api.ai import ai_bp
from apscheduler.schedulers.background import BackgroundScheduler
from apps.services.ai_service import AIService
from apps.services.socket_service import SocketService

# 创建Flask应用
app = Flask(__name__)

# 配置
app.config.update(
    # 基础配置
    SECRET_KEY='dev',  # 请在生产环境中修改为复杂的密钥
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI='mysql://cs_aiwanba_net:sQz9HSnF5ZcXj9SX@localhost:3306/cs_aiwanba_net',
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    
    # 会话配置
    SESSION_TYPE='filesystem',
    
    # 模板自动重载
    TEMPLATES_AUTO_RELOAD=True
)

# 初始化扩展
db = SQLAlchemy(app)
socketio = SocketIO(app)
migrate = Migrate(app, db)
csrf = CSRFProtect(app)
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'

# 注册蓝图
from apps.api.auth import auth_bp
from apps.api.company import company_bp
from apps.api.trading import trading_bp

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(company_bp, url_prefix='/api/company')
app.register_blueprint(trading_bp, url_prefix='/api/trading')
app.register_blueprint(bank_bp, url_prefix='/api/bank')
app.register_blueprint(news_bp, url_prefix='/api/news')
app.register_blueprint(ai_bp, url_prefix='/api/ai')

@app.route('/')
def index():
    return render_template('index.html')

# 创建定时任务调度器
scheduler = BackgroundScheduler()
scheduler.add_job(AIService.run_ai_trading, 'interval', minutes=5)
scheduler.start()

@socketio.on('connect')
def handle_connect():
    """处理客户端连接"""
    emit('connect', {'data': 'Connected'})

@socketio.on('join')
def handle_join(data):
    """加入房间"""
    room = data.get('room')
    if room:
        join_room(room)
        emit('join', {'room': room}, room=room)

@socketio.on('leave')
def handle_leave(data):
    """离开房间"""
    room = data.get('room')
    if room:
        leave_room(room)
        emit('leave', {'room': room}, room=room)

# 添加定时推送市场数据的任务
scheduler.add_job(SocketService.emit_market_update, 'interval', seconds=30)

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5010) 