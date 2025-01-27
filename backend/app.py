from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from flask_cors import CORS
from flask_socketio import SocketIO
from config import config
from services.scheduler import init_scheduler

# 初始化扩展
db = SQLAlchemy()
cache = Cache()
socketio = SocketIO()

def create_app(config_name='default'):
    app = Flask(__name__)
    
    # 加载配置
    app.config.from_object(config[config_name])
    
    # 初始化扩展
    db.init_app(app)
    cache.init_app(app)
    CORS(app)
    socketio.init_app(app, cors_allowed_origins="*")
    
    # 注册蓝图
    from routes import auth_bp, company_bp, stock_bp, bank_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(company_bp, url_prefix='/api/company')
    app.register_blueprint(stock_bp, url_prefix='/api/stock')
    app.register_blueprint(bank_bp, url_prefix='/api/bank')
    
    # 初始化定时任务
    init_scheduler()
    
    return app

app = create_app()

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5010) 