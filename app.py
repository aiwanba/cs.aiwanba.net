# 导入必要的库
from flask import Flask, jsonify
import os
import pymysql
from models import init_models

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
            # 删除所有表（如果存在）
            db.drop_all()
            print("旧表删除完成")
            
            # 创建所有表
            db.create_all()
            db.session.commit()  # 确保表创建被提交
            print("新表创建完成")
            
            # 验证表是否创建成功
            engine = db.engine
            inspector = db.inspect(engine)
            tables = inspector.get_table_names()
            print(f"已创建的表: {tables}")
            
            if 'users' not in tables:
                raise Exception("users 表创建失败")
            
            # 创建默认管理员用户
            admin = User(
                username='admin',
                email='admin@example.com',
                password_hash='admin123',
                is_ai=False
            )
            db.session.add(admin)
            try:
                db.session.commit()
                print("管理员用户创建完成")
            except Exception as e:
                db.session.rollback()
                print(f"创建管理员用户失败: {str(e)}")
                raise
            
            # 创建默认AI策略
            strategies = [
                AIStrategy(
                    name='保守策略',
                    type='conservative',
                    description='低风险、稳定收益的交易策略',
                    risk_tolerance=0.3,
                    max_position_size=0.2,
                    min_holding_period=1440,
                    profit_target=0.05,
                    stop_loss=0.03
                ),
                AIStrategy(
                    name='激进策略',
                    type='aggressive',
                    description='高风险、高收益的交易策略',
                    risk_tolerance=0.8,
                    max_position_size=0.5,
                    min_holding_period=60,
                    profit_target=0.15,
                    stop_loss=0.1
                ),
                AIStrategy(
                    name='平衡策略',
                    type='balanced',
                    description='中等风险和收益的交易策略',
                    risk_tolerance=0.5,
                    max_position_size=0.3,
                    min_holding_period=720,
                    profit_target=0.08,
                    stop_loss=0.05
                )
            ]
            for strategy in strategies:
                db.session.add(strategy)
            
            try:
                db.session.commit()
                print("AI策略创建完成")
            except Exception as e:
                db.session.rollback()
                print(f"创建AI策略失败: {str(e)}")
                raise
            
            print("数据库初始化完成")
            
        except Exception as e:
            db.session.rollback()
            print(f"初始化数据时出错: {str(e)}")
            raise

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