from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
import re
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from decimal import Decimal

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

# 初始化定时任务调度器
scheduler = BackgroundScheduler()

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

# 股票历史价格模型
class StockPrice(db.Model):
    __tablename__ = 'stock_prices'
    
    id = db.Column(db.BigInteger, primary_key=True)
    company_id = db.Column(db.BigInteger, db.ForeignKey('companies.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    open = db.Column(db.DECIMAL(10,2), nullable=False)
    high = db.Column(db.DECIMAL(10,2), nullable=False)
    low = db.Column(db.DECIMAL(10,2), nullable=False)
    close = db.Column(db.DECIMAL(10,2), nullable=False)
    volume = db.Column(db.BigInteger, nullable=False)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())

    __table_args__ = (
        db.Index('idx_company_date', 'company_id', 'date'),
    )

# AI玩家模型
class AIPlayer(db.Model):
    __tablename__ = 'ai_players'
    
    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    strategy = db.Column(db.String(50), nullable=False)  # 交易策略：保守、激进、均衡
    risk_level = db.Column(db.Integer, default=1)  # 风险等级：1-5
    min_position = db.Column(db.Integer, default=0)  # 最小持仓比例
    max_position = db.Column(db.Integer, default=100)  # 最大持仓比例
    status = db.Column(db.Integer, default=1)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

# AI交易记录
class AITradeLog(db.Model):
    __tablename__ = 'ai_trade_logs'
    
    id = db.Column(db.BigInteger, primary_key=True)
    ai_id = db.Column(db.BigInteger, db.ForeignKey('ai_players.id'), nullable=False)
    company_id = db.Column(db.BigInteger, db.ForeignKey('companies.id'), nullable=False)
    action = db.Column(db.String(20), nullable=False)  # 买入/卖出
    reason = db.Column(db.String(255), nullable=False)  # 交易原因
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())

# 存款账户模型
class DepositAccount(db.Model):
    __tablename__ = 'deposit_accounts'
    
    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 活期、定期
    amount = db.Column(db.DECIMAL(20,2), default=0.00)
    interest_rate = db.Column(db.DECIMAL(5,2), nullable=False)  # 年利率
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)  # 定期存款的到期日
    status = db.Column(db.Integer, default=1)  # 1:正常, 2:已提前支取
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

# 贷款账户模型
class LoanAccount(db.Model):
    __tablename__ = 'loan_accounts'
    
    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.DECIMAL(20,2), nullable=False)  # 贷款金额
    interest_rate = db.Column(db.DECIMAL(5,2), nullable=False)  # 年利率
    term = db.Column(db.Integer, nullable=False)  # 贷款期限(月)
    monthly_payment = db.Column(db.DECIMAL(20,2), nullable=False)  # 月供
    remaining_amount = db.Column(db.DECIMAL(20,2), nullable=False)  # 剩余本金
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.Integer, default=1)  # 1:审核中, 2:已放款, 3:已还清, 4:已拒绝
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

# 交易记录模型
class BankTransaction(db.Model):
    __tablename__ = 'bank_transactions'
    
    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 存款、取款、贷款、还款
    amount = db.Column(db.DECIMAL(20,2), nullable=False)
    account_id = db.Column(db.BigInteger, nullable=False)  # 关联的账户ID
    description = db.Column(db.String(255))
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())

# 新闻模型
class News(db.Model):
    __tablename__ = 'news'
    
    id = db.Column(db.BigInteger, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), nullable=False)  # 系统新闻、公司新闻、市场新闻
    company_id = db.Column(db.BigInteger, db.ForeignKey('companies.id'))  # 相关公司ID
    impact_level = db.Column(db.Integer, default=1)  # 影响等级：1-5
    views = db.Column(db.Integer, default=0)  # 浏览量
    status = db.Column(db.Integer, default=1)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())

# 新闻评论模型
class NewsComment(db.Model):
    __tablename__ = 'news_comments'
    
    id = db.Column(db.BigInteger, primary_key=True)
    news_id = db.Column(db.BigInteger, db.ForeignKey('news.id'), nullable=False)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    likes = db.Column(db.Integer, default=0)
    status = db.Column(db.Integer, default=1)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())

# 交易订单模型
class TradeOrder(db.Model):
    __tablename__ = 'trade_orders'
    
    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    company_id = db.Column(db.BigInteger, db.ForeignKey('companies.id'), nullable=False)
    type = db.Column(db.String(10), nullable=False)  # 买入/卖出
    price = db.Column(db.DECIMAL(10,2), nullable=False)
    shares = db.Column(db.BigInteger, nullable=False)
    status = db.Column(db.Integer, default=1)  # 1:待成交, 2:已成交, 3:已取消
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

# 交易记录模型
class TradeRecord(db.Model):
    __tablename__ = 'trade_records'
    
    id = db.Column(db.BigInteger, primary_key=True)
    order_id = db.Column(db.BigInteger, db.ForeignKey('trade_orders.id'), nullable=False)
    buyer_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    seller_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    company_id = db.Column(db.BigInteger, db.ForeignKey('companies.id'), nullable=False)
    price = db.Column(db.DECIMAL(10,2), nullable=False)
    shares = db.Column(db.BigInteger, nullable=False)
    total_amount = db.Column(db.DECIMAL(20,2), nullable=False)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())

    __table_args__ = (
        db.Index('idx_buyer', 'buyer_id'),
        db.Index('idx_seller', 'seller_id'),
        db.Index('idx_company', 'company_id'),
    )

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

# 路由：公司详情
@app.route('/company/<code>')
def company_detail(code):
    company = Company.query.filter_by(code=code).first_or_404()
    return render_template('company/detail.html', company=company)

# 路由：股票交易
@app.route('/company/<code>/trade', methods=['POST'])
@login_required
def trade_stock(code):
    company = Company.query.filter_by(code=code).first_or_404()
    
    # 获取交易参数
    trade_type = int(request.form.get('type'))  # 1:买入 2:卖出
    price = float(request.form.get('price'))
    shares = int(request.form.get('shares'))
    
    # 基本验证
    if shares % 100 != 0:
        return render_template('company/detail.html', 
                             company=company, 
                             error='交易数量必须是100的整数倍')
    
    if price <= 0:
        return render_template('company/detail.html', 
                             company=company, 
                             error='价格必须大于0')
    
    # 创建交易订单
    order = TradeOrder(
        user_id=current_user.id,
        company_id=company.id,
        type=trade_type,
        price=price,
        shares=shares,
        status=0  # 待成交
    )
    
    try:
        if trade_type == 1:  # 买入
            # 检查资金是否足够
            total_amount = price * shares
            if current_user.balance < total_amount:
                return render_template('company/detail.html', 
                                     company=company, 
                                     error='可用资金不足')
            
            # 冻结资金
            current_user.balance -= total_amount
            
        else:  # 卖出
            # 检查持仓是否足够
            holding = StockHolding.query.filter_by(
                user_id=current_user.id,
                company_id=company.id
            ).first()
            
            if not holding or holding.shares < shares:
                return render_template('company/detail.html', 
                                     company=company, 
                                     error='可用股份不足')
        
        db.session.add(order)
        db.session.commit()
        
        # 尝试撮合交易
        match_orders(company.id)
        
        return render_template('company/detail.html', 
                             company=company, 
                             success='交易委托已提交')
        
    except Exception as e:
        db.session.rollback()
        return render_template('company/detail.html', 
                             company=company, 
                             error='交易失败，请稍后重试')

def match_orders(company_id):
    """撮合交易"""
    # 获取所有未成交的买单（按价格降序）
    buy_orders = TradeOrder.query.filter_by(
        company_id=company_id,
        type=1,
        status=0
    ).order_by(TradeOrder.price.desc()).all()
    
    # 获取所有未成交的卖单（按价格升序）
    sell_orders = TradeOrder.query.filter_by(
        company_id=company_id,
        type=2,
        status=0
    ).order_by(TradeOrder.price.asc()).all()
    
    for buy_order in buy_orders:
        for sell_order in sell_orders:
            # 如果买入价大于等于卖出价，可以成交
            if buy_order.price >= sell_order.price:
                # 确定成交数量
                deal_shares = min(
                    buy_order.shares - buy_order.dealt_shares,
                    sell_order.shares - sell_order.dealt_shares
                )
                
                if deal_shares > 0:
                    # 创建成交记录
                    record = TradeRecord(
                        buyer_order_id=buy_order.id,
                        seller_order_id=sell_order.id,
                        company_id=company_id,
                        price=sell_order.price,  # 以卖方价格成交
                        shares=deal_shares,
                        amount=sell_order.price * deal_shares
                    )
                    db.session.add(record)
                    
                    # 更新订单状态
                    buy_order.dealt_shares += deal_shares
                    buy_order.dealt_amount += record.amount
                    sell_order.dealt_shares += deal_shares
                    sell_order.dealt_amount += record.amount
                    
                    # 更新订单状态
                    if buy_order.dealt_shares == buy_order.shares:
                        buy_order.status = 2  # 全部成交
                    else:
                        buy_order.status = 1  # 部分成交
                        
                    if sell_order.dealt_shares == sell_order.shares:
                        sell_order.status = 2  # 全部成交
                    else:
                        sell_order.status = 1  # 部分成交
                    
                    # 更新持仓
                    update_holdings(buy_order.user_id, sell_order.user_id, 
                                  company_id, deal_shares, sell_order.price)
                    
                    # 更新公司当前股价
                    company = Company.query.get(company_id)
                    company.current_price = sell_order.price
                    company.market_value = company.current_price * company.total_shares
                    
                    db.session.commit()

def update_holdings(buyer_id, seller_id, company_id, shares, price):
    """更新持仓记录"""
    # 更新买方持仓
    buyer_holding = StockHolding.query.filter_by(
        user_id=buyer_id,
        company_id=company_id
    ).first()
    
    if buyer_holding:
        # 计算新的平均成本
        total_cost = (buyer_holding.average_cost * buyer_holding.shares + 
                     price * shares)
        buyer_holding.shares += shares
        buyer_holding.average_cost = total_cost / buyer_holding.shares
    else:
        buyer_holding = StockHolding(
            user_id=buyer_id,
            company_id=company_id,
            shares=shares,
            average_cost=price
        )
        db.session.add(buyer_holding)
    
    # 更新卖方持仓
    seller_holding = StockHolding.query.filter_by(
        user_id=seller_id,
        company_id=company_id
    ).first()
    
    seller_holding.shares -= shares
    if seller_holding.shares == 0:
        db.session.delete(seller_holding)

# 路由：交易大厅
@app.route('/market')
def market():
    # 获取所有上市公司
    stocks = Company.query.filter_by(status=1).all()
    
    # 计算涨跌幅
    for stock in stocks:
        # 获取昨日收盘价（这里简化处理，使用当前价格）
        # TODO: 实现历史价格记录
        yesterday_price = stock.current_price
        
        stock.price_change = stock.current_price - yesterday_price
        stock.price_change_percent = (stock.price_change / yesterday_price * 100) if yesterday_price > 0 else 0
        stock.volume = 0  # TODO: 实现成交量统计
    
    return render_template('market/index.html', stocks=stocks)

# API：获取实时行情
@app.route('/api/market/stocks')
def get_market_stocks():
    stocks = Company.query.filter_by(status=1).all()
    return jsonify([{
        'code': stock.code,
        'current_price': float(stock.current_price),
        'price_change': 0,  # TODO: 实现价格变动计算
        'price_change_percent': 0,
        'volume': 0,
        'market_value': float(stock.market_value)
    } for stock in stocks])

# 路由：个人资产
@app.route('/portfolio')
@login_required
def portfolio():
    # 获取持仓信息
    holdings = StockHolding.query.filter_by(user_id=current_user.id).all()
    
    # 计算持仓市值和盈亏
    stock_value = 0
    total_profit = 0
    
    for holding in holdings:
        # 获取公司信息
        holding.company = Company.query.get(holding.company_id)
        # 计算市值
        holding.market_value = holding.shares * holding.company.current_price
        # 计算盈亏
        holding.profit = holding.market_value - (holding.shares * holding.average_cost)
        # 计算盈亏比例
        holding.profit_percent = (holding.profit / (holding.shares * holding.average_cost)) * 100
        
        stock_value += holding.market_value
        total_profit += holding.profit
    
    # 获取最近交易记录
    orders = TradeOrder.query.filter_by(user_id=current_user.id)\
        .order_by(TradeOrder.created_at.desc())\
        .limit(20)\
        .all()
    
    # 为每个订单加载公司信息
    for order in orders:
        order.company = Company.query.get(order.company_id)
    
    # 计算总资产
    total_assets = current_user.balance + stock_value
    
    return render_template('user/portfolio.html',
                         holdings=holdings,
                         orders=orders,
                         total_assets=total_assets,
                         stock_value=stock_value,
                         total_profit=total_profit)

# API：获取股票K线数据
@app.route('/api/stock/<code>/kline')
def get_stock_kline(code):
    company = Company.query.filter_by(code=code).first_or_404()
    
    # 获取最近30天的K线数据
    prices = StockPrice.query.filter_by(company_id=company.id)\
        .order_by(StockPrice.date.desc())\
        .limit(30)\
        .all()
    
    return jsonify([{
        'date': price.date.strftime('%Y-%m-%d'),
        'open': float(price.open),
        'high': float(price.high),
        'low': float(price.low),
        'close': float(price.close),
        'volume': price.volume
    } for price in prices])

# AI交易策略
def ai_trading_strategy(ai_player):
    """AI交易策略"""
    # 获取所有上市公司
    companies = Company.query.filter_by(status=1).all()
    
    for company in companies:
        # 获取公司最近的K线数据
        prices = StockPrice.query.filter_by(company_id=company.id)\
            .order_by(StockPrice.date.desc())\
            .limit(30)\
            .all()
        
        if len(prices) < 30:
            continue
            
        # 计算技术指标
        closes = [float(price.close) for price in prices]
        volumes = [price.volume for price in prices]
        
        # 5日均线
        ma5 = sum(closes[:5]) / 5
        # 10日均线
        ma10 = sum(closes[:10]) / 10
        # 当前价格
        current_price = closes[0]
        
        # 获取AI当前持仓
        holding = StockHolding.query.filter_by(
            user_id=ai_player.user_id,
            company_id=company.id
        ).first()
        
        # 交易信号判断
        if ai_player.strategy == '保守':
            # 保守策略：金叉买入，死叉卖出
            if ma5 > ma10 and not holding:  # 金叉
                create_ai_order(ai_player, company, 'buy', '金叉买入信号')
            elif ma5 < ma10 and holding:  # 死叉
                create_ai_order(ai_player, company, 'sell', '死叉卖出信号')
                
        elif ai_player.strategy == '激进':
            # 激进策略：放量上涨买入，放量下跌卖出
            volume_ratio = volumes[0] / sum(volumes[1:6]) * 5  # 当前成交量/5日平均成交量
            price_change = (closes[0] - closes[1]) / closes[1] * 100  # 价格涨跌幅
            
            if volume_ratio > 2 and price_change > 5 and not holding:  # 放量上涨
                create_ai_order(ai_player, company, 'buy', '放量上涨买入信号')
            elif volume_ratio > 2 and price_change < -5 and holding:  # 放量下跌
                create_ai_order(ai_player, company, 'sell', '放量下跌卖出信号')
                
        else:  # 均衡策略
            # 均衡策略：结合均线和成交量
            volume_ratio = volumes[0] / sum(volumes[1:6]) * 5
            
            if ma5 > ma10 and volume_ratio > 1.5 and not holding:
                create_ai_order(ai_player, company, 'buy', '均线金叉+放量买入信号')
            elif ma5 < ma10 and volume_ratio > 1.5 and holding:
                create_ai_order(ai_player, company, 'sell', '均线死叉+放量卖出信号')

def create_ai_order(ai_player, company, action, reason):
    """创建AI交易订单"""
    try:
        # 记录交易日志
        log = AITradeLog(
            ai_id=ai_player.id,
            company_id=company.id,
            action=action,
            reason=reason
        )
        db.session.add(log)
        
        # 获取用户信息
        user = User.query.get(ai_player.user_id)
        
        if action == 'buy':
            # 计算可买数量
            available_money = user.balance * (ai_player.max_position / 100)
            shares = int(available_money / company.current_price / 100) * 100
            
            if shares >= 100:  # 最小100股
                order = TradeOrder(
                    user_id=user.id,
                    company_id=company.id,
                    type=1,  # 买入
                    price=company.current_price,
                    shares=shares
                )
                db.session.add(order)
                
        else:  # sell
            holding = StockHolding.query.filter_by(
                user_id=user.id,
                company_id=company.id
            ).first()
            
            if holding:
                order = TradeOrder(
                    user_id=user.id,
                    company_id=company.id,
                    type=2,  # 卖出
                    price=company.current_price,
                    shares=holding.shares
                )
                db.session.add(order)
        
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        print(f"AI交易失败: {str(e)}")

# 定时任务：AI交易
def ai_trading_task():
    """AI交易定时任务"""
    ai_players = AIPlayer.query.filter_by(status=1).all()
    
    for ai_player in ai_players:
        ai_trading_strategy(ai_player)

# 路由：AI玩家管理
@app.route('/ai')
@login_required
def ai_index():
    ai_players = AIPlayer.query.filter_by(user_id=current_user.id).all()
    return render_template('ai/index.html', ai_players=ai_players)

# 路由：创建AI玩家
@app.route('/ai/create', methods=['POST'])
@login_required
def create_ai():
    try:
        ai = AIPlayer(
            user_id=current_user.id,
            strategy=request.form.get('strategy'),
            risk_level=int(request.form.get('risk_level')),
            min_position=int(request.form.get('min_position')),
            max_position=int(request.form.get('max_position'))
        )
        db.session.add(ai)
        db.session.commit()
        return redirect(url_for('ai_index'))
    except Exception as e:
        return render_template('ai/index.html', error='创建AI玩家失败')

# 路由：切换AI状态
@app.route('/ai/<int:ai_id>/toggle', methods=['POST'])
@login_required
def toggle_ai(ai_id):
    ai = AIPlayer.query.filter_by(id=ai_id, user_id=current_user.id).first_or_404()
    ai.status = 1 if ai.status == 0 else 0
    db.session.commit()
    return jsonify({'success': True})

# 路由：获取AI交易日志
@app.route('/ai/<int:ai_id>/logs')
@login_required
def ai_logs(ai_id):
    ai = AIPlayer.query.filter_by(id=ai_id, user_id=current_user.id).first_or_404()
    logs = AITradeLog.query.filter_by(ai_id=ai_id)\
        .order_by(AITradeLog.created_at.desc())\
        .limit(100)\
        .all()
    
    return jsonify([{
        'created_at': log.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'company_name': Company.query.get(log.company_id).name,
        'action': log.action,
        'reason': log.reason
    } for log in logs])

# 银行路由
@app.route('/bank')
@login_required
def bank_index():
    # 获取用户的存款账户
    deposits = DepositAccount.query.filter_by(user_id=current_user.id).all()
    
    # 获取用户的贷款账户
    loans = LoanAccount.query.filter_by(user_id=current_user.id).all()
    
    # 计算总资产和负债
    total_deposits = sum(float(d.amount) for d in deposits)
    total_loans = sum(float(l.remaining_amount) for l in loans)
    
    return render_template('bank/index.html',
                         deposits=deposits,
                         loans=loans,
                         total_deposits=total_deposits,
                         total_loans=total_loans)

# 存款路由
@app.route('/bank/deposit', methods=['POST'])
@login_required
def create_deposit():
    try:
        amount = float(request.form.get('amount'))
        deposit_type = request.form.get('type')
        
        if amount <= 0:
            return jsonify({'success': False, 'message': '存款金额必须大于0'})
            
        if current_user.balance < amount:
            return jsonify({'success': False, 'message': '余额不足'})
        
        # 设置利率
        if deposit_type == '活期':
            interest_rate = 0.35  # 年利率0.35%
            end_date = None
        else:  # 定期
            term = int(request.form.get('term'))  # 存期（月）
            if term == 3:
                interest_rate = 1.1
            elif term == 6:
                interest_rate = 1.3
            elif term == 12:
                interest_rate = 1.5
            else:
                interest_rate = 1.7  # 2年期
            
            end_date = (datetime.now() + timedelta(days=term*30)).date()
        
        # 创建存款账户
        deposit = DepositAccount(
            user_id=current_user.id,
            type=deposit_type,
            amount=amount,
            interest_rate=interest_rate,
            start_date=datetime.now().date(),
            end_date=end_date
        )
        
        # 扣除用户余额
        current_user.balance -= amount
        
        # 记录交易
        transaction = BankTransaction(
            user_id=current_user.id,
            type='存款',
            amount=amount,
            account_id=deposit.id,
            description=f'创建{deposit_type}存款'
        )
        
        db.session.add(deposit)
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

# 贷款申请路由
@app.route('/bank/loan/apply', methods=['POST'])
@login_required
def apply_loan():
    try:
        amount = float(request.form.get('amount'))
        term = int(request.form.get('term'))
        
        if amount <= 0:
            return jsonify({'success': False, 'message': '贷款金额必须大于0'})
        
        # 设置利率（根据贷款期限）
        if term <= 12:
            interest_rate = 4.35  # 一年以内
        elif term <= 36:
            interest_rate = 4.75  # 1-3年
        else:
            interest_rate = 4.90  # 3年以上
            
        # 计算月供（等额本息）
        monthly_rate = interest_rate / 100 / 12
        monthly_payment = amount * monthly_rate * (1 + monthly_rate)**term / ((1 + monthly_rate)**term - 1)
        
        # 创建贷款账户
        loan = LoanAccount(
            user_id=current_user.id,
            amount=amount,
            interest_rate=interest_rate,
            term=term,
            monthly_payment=monthly_payment,
            remaining_amount=amount,
            start_date=datetime.now().date(),
            end_date=(datetime.now() + timedelta(days=term*30)).date()
        )
        
        db.session.add(loan)
        db.session.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

# 新闻路由
@app.route('/news')
def news_index():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    news = News.query.filter_by(status=1)\
        .order_by(News.created_at.desc())\
        .paginate(page=page, per_page=per_page)
    
    return render_template('news/index.html', news=news)

# 新闻详情路由
@app.route('/news/<int:news_id>')
def news_detail(news_id):
    news = News.query.get_or_404(news_id)
    news.views += 1
    db.session.commit()
    
    comments = NewsComment.query.filter_by(news_id=news_id, status=1)\
        .order_by(NewsComment.created_at.desc())\
        .all()
    
    return render_template('news/detail.html', news=news, comments=comments)

# 添加评论路由
@app.route('/news/<int:news_id>/comment', methods=['POST'])
@login_required
def add_comment(news_id):
    content = request.form.get('content')
    if not content:
        return jsonify({'success': False, 'message': '评论内容不能为空'})
    
    comment = NewsComment(
        news_id=news_id,
        user_id=current_user.id,
        content=content
    )
    
    db.session.add(comment)
    db.session.commit()
    
    return jsonify({'success': True})

# 生成新闻的定时任务
def generate_news():
    """定时生成新闻"""
    try:
        # 获取所有活跃公司
        companies = Company.query.filter_by(status=1).all()
        
        for company in companies:
            # 获取公司最近的交易数据
            recent_prices = StockPrice.query.filter_by(company_id=company.id)\
                .order_by(StockPrice.date.desc())\
                .limit(2)\
                .all()
            
            if len(recent_prices) < 2:
                continue
            
            # 计算涨跌幅
            price_change = (float(recent_prices[0].close) - float(recent_prices[1].close)) / float(recent_prices[1].close) * 100
            
            # 根据涨跌幅生成新闻
            if abs(price_change) >= 5:  # 涨跌幅超过5%
                title = f"{company.name}股价大{('涨' if price_change > 0 else '跌')}，单日涨幅达{abs(price_change):.2f}%"
                content = f"""
                今日，{company.name}（{company.code}）股价出现大幅波动，
                收盘价为{recent_prices[0].close}元，较前一交易日{('上涨' if price_change > 0 else '下跌')}{abs(price_change):.2f}%。
                成交量为{recent_prices[0].volume}股，市值达到{company.market_value}元。
                """
                
                news = News(
                    title=title,
                    content=content,
                    type='市场新闻',
                    company_id=company.id,
                    impact_level=min(5, int(abs(price_change) / 2))
                )
                db.session.add(news)
        
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        print(f"生成新闻失败: {str(e)}")

# 计算存款利息
def calculate_deposit_interest():
    """计算存款利息（每天执行）"""
    try:
        deposits = DepositAccount.query.filter_by(status=1).all()
        
        for deposit in deposits:
            # 计算日利率
            daily_rate = float(deposit.interest_rate) / 100 / 365
            
            # 计算利息
            interest = float(deposit.amount) * daily_rate
            
            # 活期存款直接加入余额
            if deposit.type == '活期':
                user = User.query.get(deposit.user_id)
                user.balance = float(user.balance) + interest
                
                # 记录交易
                transaction = BankTransaction(
                    user_id=user.id,
                    type='利息',
                    amount=interest,
                    account_id=deposit.id,
                    description='活期存款利息'
                )
                db.session.add(transaction)
            
            # 定期存款到期处理
            elif deposit.end_date and deposit.end_date <= datetime.now().date():
                user = User.query.get(deposit.user_id)
                total_interest = float(deposit.amount) * float(deposit.interest_rate) / 100 * \
                    ((deposit.end_date - deposit.start_date).days / 365)
                
                user.balance = float(user.balance) + float(deposit.amount) + total_interest
                deposit.status = 2  # 已提前支取
                
                # 记录交易
                transaction = BankTransaction(
                    user_id=user.id,
                    type='利息',
                    amount=total_interest,
                    account_id=deposit.id,
                    description='定期存款到期'
                )
                db.session.add(transaction)
        
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        print(f"计算存款利息失败: {str(e)}")

# 处理贷款还款
def process_loan_payment():
    """处理贷款还款（每月1号执行）"""
    try:
        loans = LoanAccount.query.filter_by(status=2).all()  # 已放款的贷款
        
        for loan in loans:
            user = User.query.get(loan.user_id)
            
            # 如果余额足够还款
            if float(user.balance) >= float(loan.monthly_payment):
                user.balance = float(user.balance) - float(loan.monthly_payment)
                loan.remaining_amount = float(loan.remaining_amount) - \
                    (float(loan.monthly_payment) - float(loan.monthly_payment) * \
                    float(loan.interest_rate) / 100 / 12)
                
                # 记录交易
                transaction = BankTransaction(
                    user_id=user.id,
                    type='还款',
                    amount=float(loan.monthly_payment),
                    account_id=loan.id,
                    description='贷款月供'
                )
                db.session.add(transaction)
                
                # 判断是否已还清
                if float(loan.remaining_amount) <= 0:
                    loan.status = 3  # 已还清
            else:
                # TODO: 处理逾期
                pass
        
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        print(f"处理贷款还款失败: {str(e)}")

# 添加定时任务
def init_scheduler():
    """初始化定时任务"""
    # AI交易（每5分钟执行一次）
    scheduler.add_job(
        ai_trading_task,
        trigger=CronTrigger(minute='*/5'),
        id='ai_trading',
        replace_existing=True
    )
    
    # 新闻生成（每小时执行一次）
    scheduler.add_job(
        generate_news,
        trigger=CronTrigger(minute='0'),
        id='generate_news',
        replace_existing=True
    )
    
    # 计算存款利息（每天0点执行）
    scheduler.add_job(
        calculate_deposit_interest,
        trigger=CronTrigger(hour='0'),
        id='calculate_interest',
        replace_existing=True
    )
    
    # 处理贷款还款（每月1号0点执行）
    scheduler.add_job(
        process_loan_payment,
        trigger=CronTrigger(day='1', hour='0'),
        id='loan_payment',
        replace_existing=True
    )
    
    # 启动调度器
    scheduler.start()

# 在应用启动时初始化定时任务
if __name__ == '__main__':
    init_scheduler()
    app.run(host='0.0.0.0', port=5010, debug=True) 