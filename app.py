from flask import Flask, render_template, jsonify
from apps.extensions import init_extensions, db, socketio
from flask_socketio import emit, join_room, leave_room
from apscheduler.schedulers.background import BackgroundScheduler
import pymysql

# 使用 PyMySQL 替代 MySQLdb
pymysql.install_as_MySQLdb()

def create_app():
    """创建Flask应用"""
    app = Flask(__name__)
    
    # 配置
    app.config.update(
        # 基础配置
        SECRET_KEY='dev',  # 请在生产环境中修改为复杂的密钥
        
        # 数据库配置
        SQLALCHEMY_DATABASE_URI='mysql+pymysql://cs_aiwanba_net:sQz9HSnF5ZcXj9SX@localhost:3306/cs_aiwanba_net',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        
        # 会话配置
        SESSION_TYPE='filesystem',
        
        # 模板自动重载
        TEMPLATES_AUTO_RELOAD=True
    )
    
    # 初始化扩展
    init_extensions(app)
    
    # 注册蓝图
    from apps.api.auth import auth_bp
    from apps.api.company import company_bp
    from apps.api.trading import trading_bp
    from apps.api.bank import bank_bp
    from apps.api.news import news_bp
    from apps.api.ai import ai_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(company_bp, url_prefix='/api/company')
    app.register_blueprint(trading_bp, url_prefix='/api/trading')
    app.register_blueprint(bank_bp, url_prefix='/api/bank')
    app.register_blueprint(news_bp, url_prefix='/api/news')
    app.register_blueprint(ai_bp, url_prefix='/api/ai')
    
    # 注册错误处理
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'message': '资源不存在'}), 404
    
    @app.errorhandler(500)
    def server_error(error):
        return jsonify({'message': '服务器错误'}), 500
    
    # 注册WebSocket事件处理
    from apps.services.socket_service import SocketService
    
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
    
    return app

if __name__ == '__main__':
    app = create_app()
    socketio.run(app, debug=True, host='0.0.0.0', port=5010) 