from flask import Flask, render_template
from config.settings import Config
from models import db
import logging
from routes.auth import auth_bp
from routes.company import company_bp
from routes.bank import bank_bp
from routes.news import news_bp
from routes.social import social_bp
from routes.analysis import analysis_bp
from routes.trading import trading_bp

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 创建Flask应用
app = Flask(__name__)

# 加载配置
app.config.from_object(Config)

# 初始化数据库连接
db.init_app(app)

# 注册蓝图
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(company_bp, url_prefix='/company')
app.register_blueprint(bank_bp, url_prefix='/bank')
app.register_blueprint(news_bp, url_prefix='/news')
app.register_blueprint(social_bp, url_prefix='/social')
app.register_blueprint(analysis_bp, url_prefix='/analysis')
app.register_blueprint(trading_bp, url_prefix='/trading')

# 注册路由
@app.route('/')
def index():
    """首页路由"""
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5010, debug=True) 