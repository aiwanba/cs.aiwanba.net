from flask import Flask
from models import db
from auth import auth
from trade import trade  # 导入trade模块

# 创建Flask应用
app = Flask(__name__)

# 配置数据库连接
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://cs_aiwanba_net:sQz9HSnF5ZcXj9SX@localhost:3306/cs_aiwanba_net'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化数据库
db.init_app(app)

# 注册auth蓝图
app.register_blueprint(auth, url_prefix='/api/auth')

# 注册trade蓝图
app.register_blueprint(trade, url_prefix='/api/trade')

# 首页路由
@app.route('/')
def index():
    return '欢迎来到股票投资模拟游戏！'

# 启动应用
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5010) 