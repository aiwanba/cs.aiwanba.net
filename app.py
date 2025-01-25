from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
import re

# 创建Flask应用
app = Flask(__name__)

# 配置
app.config['SECRET_KEY'] = os.urandom(24)  # 设置密钥
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://cs_aiwanba_net:sQz9HSnF5ZcXj9SX@localhost/cs_aiwanba_net'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化数据库
db = SQLAlchemy(app)

# 初始化登录管理器
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# 用户模型
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.BigInteger, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    nickname = db.Column(db.String(50), nullable=False)
    avatar = db.Column(db.String(255))
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    balance = db.Column(db.DECIMAL(20,2), default=0.00)
    status = db.Column(db.Integer, default=1)
    is_ai = db.Column(db.Integer, default=0)

# 公司模型
class Company(db.Model):
    __tablename__ = 'companies'
    
    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(10), unique=True, nullable=False)
    description = db.Column(db.Text)
    industry = db.Column(db.String(50), nullable=False)
    registered_capital = db.Column(db.DECIMAL(20,2), nullable=False)
    total_shares = db.Column(db.BigInteger, nullable=False)
    current_price = db.Column(db.DECIMAL(10,2), default=0.00)
    market_value = db.Column(db.DECIMAL(20,2), default=0.00)
    creator_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.Integer, default=1)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

# 股票持仓模型
class StockHolding(db.Model):
    __tablename__ = 'stock_holdings'
    
    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    company_id = db.Column(db.BigInteger, db.ForeignKey('companies.id'), nullable=False)
    shares = db.Column(db.BigInteger, nullable=False)
    average_cost = db.Column(db.DECIMAL(10,2), nullable=False)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 路由：首页
@app.route('/')
def index():
    return render_template('index.html')

# 路由：登录
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        
        return render_template('login.html', error='用户名或密码错误')
    
    return render_template('login.html')

# 路由：注册
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        nickname = request.form.get('nickname')
        email = request.form.get('email')
        
        # 检查用户名是否已存在
        if User.query.filter_by(username=username).first():
            return render_template('register.html', error='用户名已存在')
        
        # 检查邮箱是否已存在
        if User.query.filter_by(email=email).first():
            return render_template('register.html', error='邮箱已被注册')
        
        # 创建新用户
        new_user = User(
            username=username,
            password=generate_password_hash(password),
            nickname=nickname,
            email=email,
            balance=10000.00  # 给新用户初始资金10000
        )
        
        try:
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            return render_template('register.html', error='注册失败，请稍后重试')
    
    return render_template('register.html')

# 路由：退出登录
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# 路由：创建公司
@app.route('/company/create', methods=['GET', 'POST'])
@login_required
def create_company():
    if request.method == 'POST':
        # 获取表单数据
        name = request.form.get('name')
        code = request.form.get('code')
        description = request.form.get('description')
        industry = request.form.get('industry')
        registered_capital = float(request.form.get('registered_capital'))
        total_shares = int(request.form.get('total_shares'))
        price = float(request.form.get('price'))
        
        # 验证股票代码格式
        if not re.match(r'^[A-Z0-9]{6}$', code):
            return render_template('company/create.html', error='股票代码必须是6位大写字母或数字')
        
        # 检查股票代码是否已存在
        if Company.query.filter_by(code=code).first():
            return render_template('company/create.html', error='股票代码已存在')
        
        # 验证发行总额
        if total_shares * price != registered_capital:
            return render_template('company/create.html', error='发行总额必须等于注册资本')
        
        # 检查用户资金是否足够
        if current_user.balance < registered_capital:
            return render_template('company/create.html', error='您的资金不足，无法创建公司')
        
        try:
            # 创建公司
            company = Company(
                name=name,
                code=code,
                description=description,
                industry=industry,
                registered_capital=registered_capital,
                total_shares=total_shares,
                current_price=price,
                market_value=registered_capital,
                creator_id=current_user.id
            )
            db.session.add(company)
            
            # 扣除用户资金
            current_user.balance -= registered_capital
            
            # 创建创始人持股记录
            holding = StockHolding(
                user_id=current_user.id,
                company_id=company.id,
                shares=total_shares,
                average_cost=price
            )
            db.session.add(holding)
            
            db.session.commit()
            return redirect(url_for('company_detail', code=code))
            
        except Exception as e:
            db.session.rollback()
            return render_template('company/create.html', error='创建失败，请稍后重试')
    
    return render_template('company/create.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5010, debug=True) 