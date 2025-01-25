from flask import Flask, render_template
from config.settings import Config
from models import init_db
from routes.auth import auth_bp
from routes.company import company_bp

# 创建Flask应用
app = Flask(__name__)
app.config.from_object(Config)

# 初始化数据库
init_db(app)

# 注册蓝图
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(company_bp, url_prefix='/company')

# 注册路由
@app.route('/')
def index():
    """首页路由"""
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5010, debug=True) 