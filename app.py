from flask import Flask, jsonify
from datetime import datetime
from models import db
from routes.company import company_bp
from routes.trading import trading_bp
from routes.bank import bank_bp
from routes.notification import notification_bp

app = Flask(__name__)

# 数据库配置
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://cs_aiwanba_net:sQz9HSnF5ZcXj9SX@localhost:3306/cs_aiwanba_net'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# 注册蓝图
app.register_blueprint(company_bp)
app.register_blueprint(trading_bp)
app.register_blueprint(bank_bp)
app.register_blueprint(notification_bp)

# 基础路由
@app.route('/')
def index():
    return jsonify({
        'status': 'success',
        'message': '股票交易游戏API服务正常运行'
    })

if __name__ == '__main__':
    app.run(port=5010) 