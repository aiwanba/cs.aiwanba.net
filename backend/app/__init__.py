from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from redis import Redis
from .config import config

# 初始化扩展
db = SQLAlchemy()
jwt = JWTManager()
redis_client = None

def create_app(config_name='default'):
    app = Flask(__name__)
    
    # 加载配置
    app.config.from_object(config[config_name])
    
    # 初始化扩展
    db.init_app(app)
    jwt.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": app.config['CORS_ORIGINS']}})
    
    # 初始化Redis
    global redis_client
    redis_client = Redis.from_url(app.config['REDIS_URL'])
    
    # 注册蓝图
    from .api import auth_bp, company_bp, bank_bp, trade_bp, message_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(company_bp, url_prefix='/api/companies')
    app.register_blueprint(bank_bp, url_prefix='/api/banks')
    app.register_blueprint(trade_bp, url_prefix='/api/trades')
    app.register_blueprint(message_bp, url_prefix='/api/messages')
    
    return app 