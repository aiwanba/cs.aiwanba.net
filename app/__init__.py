from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit, join_room, leave_room
from config import Config

# 初始化Flask应用
app = Flask(__name__)
app.config.from_object('config.production')

# 初始化数据库
db = SQLAlchemy(app)

# 初始化WebSocket
socketio = SocketIO(app)

from app.services.websocket_service import WebSocketService

# 初始化WebSocket服务
websocket_service = WebSocketService()

# 注册WebSocket事件处理器
@socketio.on('connect')
def handle_connect():
    websocket_service.handle_connect()

@socketio.on('disconnect')
def handle_disconnect():
    websocket_service.handle_disconnect()

@socketio.on('subscribe_company')
@websocket_service.authenticate_socket
def handle_subscribe_company(data):
    """订阅特定公司的更新"""
    company_id = data.get('company_id')
    if company_id:
        join_room(f'company_{company_id}')
        emit('subscribed', {'company_id': company_id})

@socketio.on('unsubscribe_company')
@websocket_service.authenticate_socket
def handle_unsubscribe_company(data):
    """取消订阅特定公司的更新"""
    company_id = data.get('company_id')
    if company_id:
        leave_room(f'company_{company_id}')
        emit('unsubscribed', {'company_id': company_id})

@socketio.on('get_market_data')
@websocket_service.authenticate_socket
def handle_get_market_data():
    """获取市场数据"""
    market_data = websocket_service._get_market_data()
    emit('market_data', market_data)

# 导入路由
from app.routes import company_routes, stock_routes, bank_routes
app.register_blueprint(company_routes.bp)
app.register_blueprint(stock_routes.bp)
app.register_blueprint(bank_routes.bp) 