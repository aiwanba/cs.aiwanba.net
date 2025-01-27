import pymysql
pymysql.install_as_MySQLdb()

from flask import Flask, jsonify
from config import config
from extensions import db, cache, cors, socketio

def create_app(config_name='default'):
    app = Flask(__name__)
    
    # 加载配置
    app.config.from_object(config[config_name])
    
    # 初始化扩展
    db.init_app(app)
    cache.init_app(app)
    cors.init_app(app)
    socketio.init_app(app, cors_allowed_origins=["http://localhost:3000"])
    
    # 添加根路由
    @app.route('/')
    def index():
        return jsonify({
            'status': 'ok',
            'message': 'Stock Trading Game API Server'
        })
    
    # 注册蓝图
    from routes import auth_bp, company_bp, stock_bp, bank_bp, dashboard_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(company_bp, url_prefix='/api/company')
    app.register_blueprint(stock_bp, url_prefix='/api/stock')
    app.register_blueprint(bank_bp, url_prefix='/api/bank')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    
    return app

app = create_app()

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5010) 