# 导入必要的库
from flask import Flask, jsonify
import os
import pymysql
from models import init_models
from flask_migrate import Migrate

# 安装 PyMySQL
pymysql.install_as_MySQLdb()

# 创建Flask应用实例
app = Flask(__name__)

# 配置数据库连接
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://cs_aiwanba_net:sQz9HSnF5ZcXj9SX@localhost:3306/cs_aiwanba_net?charset=utf8mb4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_recycle': 280,
    'pool_timeout': 20,
    'pool_size': 5
}
app.config['SECRET_KEY'] = os.urandom(24)

# 初始化数据库
db = init_models(app)
migrate = Migrate(app, db)  # 添加迁移支持

# 导入所有模型（在初始化数据库之后）
from models.user import User
from models.company import Company
from models.stock import Stock
from models.bank import BankAccount, BankTransaction
from models.transaction import Transaction, Order
from models.ai_strategy import AIStrategy, AITrader

# 创建基本路由
@app.route('/')
def index():
    return jsonify({
        "status": "success",
        "message": "股票交易游戏API服务正在运行"
    })

# 导入蓝图和定时任务
from api.bank_api import bank_bp
from api.transaction_api import transaction_bp
from api.stock_api import stock_bp
from api.ai_trading_api import ai_trading_bp
from tasks.stock_price_updater import setup_stock_price_updater

# 注册蓝图
app.register_blueprint(bank_bp, url_prefix='/api/bank')
app.register_blueprint(transaction_bp, url_prefix='/api/transaction')
app.register_blueprint(stock_bp, url_prefix='/api/stock')
app.register_blueprint(ai_trading_bp, url_prefix='/api/ai-trading')

def init_db():
    """初始化数据库"""
    with app.app_context():
        try:
            inspector = db.inspect(db.engine)
            if not inspector.has_table('users'):
                db.create_all()
                print("数据库表创建完成")
            else:
                print("数据库表已存在，跳过创建")
            
            # 初始化数据（无论表是否为空）
            init_data()
        except Exception as e:
            db.session.rollback()
            print(f"初始化数据时出错: {str(e)}")
            raise

def init_data():
    """初始化数据"""
    if not User.query.first():
        # 创建默认管理员用户
        admin = User(
            username='admin',
            email='admin@example.com',
            password_hash='admin123',
            is_ai=False
        )
        db.session.add(admin)
        db.session.flush()  # 确保 admin.id 可用
        
        # 创建默认公司
        company = Company(
            name='默认公司',
            owner_id=admin.id,
            initial_capital=1000000,
            current_stock_price=100,
            total_shares=10000
        )
        db.session.add(company)
        db.session.flush()  # 确保 company.id 可用
        
        # 创建默认股票
        stock = Stock(
            company_id=company.id,  # 使用 company.id
            owner_id=admin.id,      # 使用 admin.id
            shares=10000,
            current_price=100
        )
        db.session.add(stock)
        
        try:
            db.session.commit()
            print("初始化数据完成")
        except Exception as e:
            db.session.rollback()
            print(f"初始化数据失败: {str(e)}")
            raise
    else:
        print("数据库已有数据，跳过初始化")

def test_db_connection():
    """测试数据库连接"""
    try:
        with app.app_context():  # 添加应用上下文
            engine = db.engine
            connection = engine.connect()
            connection.close()
            print("数据库连接测试成功")
            return True
    except Exception as e:
        print(f"数据库连接测试失败: {str(e)}")
        return False

if __name__ == '__main__':
    # 测试数据库连接
    if not test_db_connection():
        print("数据库连接失败，程序退出")
        exit(1)
        
    # 初始化数据库
    init_db()
    
    # 启动定时任务，传入app实例
    setup_stock_price_updater(app)
    
    # 启动应用
    app.run(host='0.0.0.0', port=5010, debug=True) 