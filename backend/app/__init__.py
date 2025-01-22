from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

# 创建数据库实例
db = SQLAlchemy()

def create_app():
    """
    创建并配置Flask应用
    """
    # 创建Flask应用实例
    app = Flask(__name__)
    
    # 配置跨域资源共享
    CORS(app)
    
    # 从config.py加载配置
    app.config.from_object('config.Config')
    
    # 初始化数据库
    db.init_app(app)
    
    # 注册蓝图
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    return app