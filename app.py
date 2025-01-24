from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from config import Config
import logging
from logging.handlers import RotatingFileHandler
import os

# 初始化Flask应用
app = Flask(__name__)
app.config.from_object('config.production')

# 初始化数据库
db = SQLAlchemy(app)

# 初始化WebSocket
socketio = SocketIO(app)

# 配置日志
if not os.path.exists('logs'):
    os.mkdir('logs')
file_handler = RotatingFileHandler('logs/cs_aiwanba.log', maxBytes=10240, backupCount=10)
file_handler.setFormatter(logging.Formatter(
    '[%(asctime)s] [%(levelname)s] [%(module)s] [%(request_id)s] %(message)s'
))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)
app.logger.info('CS AIWANBA startup')

# 注册蓝图
from app.routes import company_routes, stock_routes, bank_routes
app.register_blueprint(company_routes.bp)
app.register_blueprint(stock_routes.bp)
app.register_blueprint(bank_routes.bp)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5010, debug=True) 