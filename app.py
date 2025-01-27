from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
import re
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from decimal import Decimal
import logging
from sqlalchemy import func

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('app.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

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

# ============ 工具函数定义 ============

def update_holdings(buyer_id, seller_id, company_id, shares, price):
    """更新买卖双方的持仓记录"""
    try:
        # 更新买方持仓
        buyer_holding = StockHolding.query.filter_by(
            user_id=buyer_id,
            company_id=company_id
        ).first()
        
        if buyer_holding:
            # 更新现有持仓
            total_cost = buyer_holding.shares * buyer_holding.average_cost + price * shares
            buyer_holding.shares += shares
            buyer_holding.average_cost = total_cost / buyer_holding.shares
        else:
            # 创建新持仓
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
        
        if seller_holding:
            seller_holding.shares -= shares
            if seller_holding.shares == 0:
                db.session.delete(seller_holding)
        
        db.session.commit()
        logging.info(f"更新持仓成功 - 买方:{buyer_id}, 卖方:{seller_id}, 数量:{shares}")
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"更新持仓失败: {str(e)}", exc_info=True)
        raise

def match_orders(company_id):
    """撮合交易"""
    try:
        # 获取所有未完全成交的买单（按价格降序，时间优先）
        buy_orders = TradeOrder.query.filter(
            TradeOrder.company_id == company_id,
            TradeOrder.type == 1,  # 买单
            TradeOrder.status.in_([0, 1]),  # 未成交或部分成交，排除已撤单(3)
            TradeOrder.shares > TradeOrder.dealt_shares
        ).order_by(
            TradeOrder.price.desc(),
            TradeOrder.created_at.asc()
        ).all()
        
        # 获取所有未完全成交的卖单（按价格升序，时间优先）
        sell_orders = TradeOrder.query.filter(
            TradeOrder.company_id == company_id,
            TradeOrder.type == 2,  # 卖单
            TradeOrder.status.in_([0, 1]),  # 未成交或部分成交，排除已撤单(3)
            TradeOrder.shares > TradeOrder.dealt_shares
        ).order_by(
            TradeOrder.price.asc(),
            TradeOrder.created_at.asc()
        ).all()
        
        company = db.session.get(Company, company_id)
        today = datetime.now().date()
        
        for buy_order in buy_orders:
            for sell_order in sell_orders:
                # 如果买入价大于等于卖出价，可以成交
                if buy_order.price >= sell_order.price:
                    # 计算本次成交数量
                    available_buy = buy_order.shares - buy_order.dealt_shares
                    available_sell = sell_order.shares - sell_order.dealt_shares
                    deal_shares = min(available_buy, available_sell)
                    
                    if deal_shares > 0:
                        # 以卖方价格成交
                        deal_price = sell_order.price
                        deal_amount = deal_price * deal_shares
                        
                        # 创建成交记录
                        record = TradeRecord(
                            buyer_order_id=buy_order.id,
                            seller_order_id=sell_order.id,
                            company_id=company_id,
                            price=deal_price,
                            shares=deal_shares,
                            amount=deal_amount
                        )
                        db.session.add(record)
                        
                        # 更新订单状态
                        buy_order.dealt_shares += deal_shares
                        buy_order.dealt_amount += deal_amount
                        sell_order.dealt_shares += deal_shares
                        sell_order.dealt_amount += deal_amount
                        
                        # 更新订单状态
                        for order in [buy_order, sell_order]:
                            if order.dealt_shares == order.shares:
                                order.status = 2  # 完全成交
                            else:
                                order.status = 1  # 部分成交
                        
                        # 更新持仓
                        update_holdings(buy_order.user_id, sell_order.user_id, 
                                     company_id, deal_shares, deal_price)
                        
                        # 更新公司当前价格
                        company.current_price = deal_price
                        company.market_value = company.current_price * company.total_shares
                        
                        # 更新今日成交量
                        stock_price = StockPrice.query.filter_by(
                            company_id=company_id,
                            date=today
                        ).first()
                        
                        if stock_price:
                            stock_price.volume += deal_shares
                            stock_price.close = deal_price
                            if deal_price > stock_price.high:
                                stock_price.high = deal_price
                            if deal_price < stock_price.low:
                                stock_price.low = deal_price
                        
                        db.session.commit()
                        logging.info(f"撮合成功 - 买方:{buy_order.id}, 卖方:{sell_order.id}, "
                                   f"价格:{deal_price}, 数量:{deal_shares}")
                        
                        # 如果买单已完全成交，跳出内层循环
                        if buy_order.status == 2:
                            break
                else:
                    # 如果买入价小于卖出价，无法成交，跳出内层循环
                    break
                    
    except Exception as e:
        db.session.rollback()
        logging.error(f"撮合交易失败: {str(e)}", exc_info=True)

# ============ 数据库模型定义 ============

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
class AIStrategy(db.Model):
    __tablename__ = 'ai_strategies'
    
    id = db.Column(db.BigInteger, primary_key=True)
    ai_user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    strategy_type = db.Column(db.Integer, nullable=False)  # 1:保守, 2:稳健, 3:激进
    risk_level = db.Column(db.Integer, nullable=False)  # 风险等级(1-5)
    min_position = db.Column(db.Integer, nullable=False, default=0)  # 最小持仓比例(%)
    max_position = db.Column(db.Integer, nullable=False, default=100)  # 最大持仓比例(%)
    min_price = db.Column(db.DECIMAL(10,2))  # 最低买入价
    max_price = db.Column(db.DECIMAL(10,2))  # 最高买入价
    position_limit = db.Column(db.Integer, default=100)  # 持仓上限(%)
    status = db.Column(db.Integer, default=1)  # 0:禁用, 1:启用
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    __table_args__ = (
        db.Index('idx_ai_user', 'ai_user_id'),
    )

# AI交易记录
class AITradeLog(db.Model):
    __tablename__ = 'ai_trade_logs'
    
    id = db.Column(db.BigInteger, primary_key=True)
    ai_id = db.Column(db.BigInteger, db.ForeignKey('ai_strategies.id'), nullable=False)
    company_id = db.Column(db.BigInteger, db.ForeignKey('companies.id'), nullable=False)
    action = db.Column(db.String(50), nullable=False)  # buy/sell
    reason = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())

    ai_strategy = db.relationship('AIStrategy', backref='trade_logs')
    company = db.relationship('Company')

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

# 新闻模型
class News(db.Model):
    __tablename__ = 'news'
    
    id = db.Column(db.BigInteger, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    type = db.Column(db.Integer, nullable=False)  # 1:系统新闻, 2:公司公告, 3:市场动态
    company_id = db.Column(db.BigInteger, db.ForeignKey('companies.id'))
    impact_score = db.Column(db.Integer, default=0)  # 影响力评分
    status = db.Column(db.Integer, default=1)  # 0:隐藏, 1:显示
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())

    __table_args__ = (
        db.Index('idx_company', 'company_id'),
    )

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
    type = db.Column(db.Integer, nullable=False)  # 1:买入 2:卖出
    price = db.Column(db.DECIMAL(10,2), nullable=False)
    shares = db.Column(db.BigInteger, nullable=False)
    dealt_shares = db.Column(db.BigInteger, default=0)
    dealt_amount = db.Column(db.DECIMAL(20,2), default=0)
    status = db.Column(db.Integer, default=0)  # 0:未成交 1:部分成交 2:完全成交 3:已撤单
    cancel_time = db.Column(db.DateTime)  # 撤单时间
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

# 交易记录模型
class TradeRecord(db.Model):
    __tablename__ = 'trade_records'
    
    id = db.Column(db.BigInteger, primary_key=True)
    buyer_order_id = db.Column(db.BigInteger, db.ForeignKey('trade_orders.id'), nullable=False)
    seller_order_id = db.Column(db.BigInteger, db.ForeignKey('trade_orders.id'), nullable=False)
    company_id = db.Column(db.BigInteger, db.ForeignKey('companies.id'), nullable=False)
    price = db.Column(db.DECIMAL(10,2), nullable=False)
    shares = db.Column(db.BigInteger, nullable=False)
    amount = db.Column(db.DECIMAL(20,2), nullable=False)  # 成交金额
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())

    __table_args__ = (
        db.Index('idx_buyer_order', 'buyer_order_id'),
        db.Index('idx_seller_order', 'seller_order_id'),
        db.Index('idx_company', 'company_id')
    )

# 聊天消息模型
class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.BigInteger, primary_key=True)
    sender_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.BigInteger, db.ForeignKey('users.id'))  # NULL表示群发
    content = db.Column(db.Text, nullable=False)
    type = db.Column(db.Integer, nullable=False)  # 1:文本, 2:图片, 3:表情
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())

    __table_args__ = (
        db.Index('idx_sender', 'sender_id'),
        db.Index('idx_receiver', 'receiver_id'),
    )

# 团队模型
class Team(db.Model):
    __tablename__ = 'teams'
    
    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    leader_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    description = db.Column(db.String(200))
    member_limit = db.Column(db.Integer, default=10)
    status = db.Column(db.Integer, default=1)  # 0:解散, 1:正常
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    __table_args__ = (
        db.Index('idx_leader', 'leader_id'),
    )

# 团队成员模型
class TeamMember(db.Model):
    __tablename__ = 'team_members'
    
    id = db.Column(db.BigInteger, primary_key=True)
    team_id = db.Column(db.BigInteger, db.ForeignKey('teams.id'), nullable=False)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    role = db.Column(db.Integer, default=0)  # 0:成员, 1:管理员
    contribution = db.Column(db.DECIMAL(20,2), default=0.00)
    joined_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())

    __table_args__ = (
        db.UniqueConstraint('team_id', 'user_id', name='idx_team_user'),
    )

# 系统配置模型
class SystemConfig(db.Model):
    __tablename__ = 'system_configs'
    
    id = db.Column(db.BigInteger, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=False)
    description = db.Column(db.String(200))
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

# 定时任务装饰器
def with_app_context(func):
    """确保定时任务在应用上下文中运行的装饰器"""
    def wrapper(*args, **kwargs):
        with app.app_context():
            return func(*args, **kwargs)
    return wrapper

# 定时任务函数定义
@with_app_context
def init_daily_prices():
    """每天开盘时初始化当日价格记录"""
    try:
        today = datetime.now().date()
        companies = Company.query.filter_by(status=1).all()
        
        for company in companies:
            # 检查是否已有今日记录
            exists = StockPrice.query.filter_by(
                company_id=company.id,
                date=today
            ).first()
            
            if not exists:
                # 创建今日价格记录
                price = StockPrice(
                    company_id=company.id,
                    date=today,
                    open=company.current_price,
                    high=company.current_price,
                    low=company.current_price,
                    close=company.current_price,
                    volume=0
                )
                db.session.add(price)
        
        db.session.commit()
        logging.info(f"初始化{len(companies)}个公司的每日价格记录")
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"初始化每日价格记录失败: {str(e)}", exc_info=True)

@with_app_context
def ai_trading_task():
    """AI交易任务，每5分钟执行一次"""
    try:
        # 获取所有启用的AI策略
        ai_strategies = AIStrategy.query.filter_by(status=1).all()
        
        for ai in ai_strategies:
            # 获取AI用户
            ai_user = User.query.get(ai.ai_user_id)
            
            # 获取所有公司
            companies = Company.query.filter_by(status=1).all()
            
            for company in companies:
                # 根据策略类型计算风险系数
                risk_factor = {
                    1: 0.3,  # 保守型
                    2: 0.6,  # 稳健型
                    3: 1.0   # 激进型
                }.get(ai.strategy_type, 0.6)
                
                # 根据风险等级调整交易量
                trade_volume = int(100 * (ai.risk_level / 5) * risk_factor)
                
                # 检查价格是否在AI的交易范围内
                if (ai.min_price and company.current_price < ai.min_price) or \
                   (ai.max_price and company.current_price > ai.max_price):
                    continue
                
                # 获取当前持仓
                holding = StockHolding.query.filter_by(
                    user_id=ai_user.id,
                    company_id=company.id
                ).first()
                
                current_position = 0
                if holding:
                    current_position = (holding.shares * company.current_price) / ai_user.balance * 100
                
                # 获取最近的价格历史
                recent_prices = StockPrice.query.filter_by(company_id=company.id)\
                    .order_by(StockPrice.date.desc())\
                    .limit(5).all()
                
                # 计算价格趋势
                price_trend = 0
                if len(recent_prices) >= 5:
                    trend = sum(1 if recent_prices[i].close > recent_prices[i+1].close else -1 
                               for i in range(len(recent_prices)-1))
                price_trend = trend / (len(recent_prices)-1)  # 归一化到[-1,1]
                
                # 根据策略类型和风险等级决定操作
                if current_position < ai.min_position:  # 持仓不足，考虑买入
                    # 根据趋势调整买入意愿
                    if price_trend < -0.5 and ai.strategy_type == 1:  # 保守型在下跌趋势时不买入
                        continue
                    
                    amount = min(
                        ai_user.balance * risk_factor,  # 根据风险系数限制单次交易金额
                        company.current_price * trade_volume
                    )
                    
                    if amount >= company.current_price:
                        # 记录交易日志
                        log = AITradeLog(
                            ai_id=ai.id,
                            company_id=company.id,
                            action='buy',
                            reason=f'当前持仓{current_position:.2f}%低于最小持仓{ai.min_position}%，'
                                   f'价格趋势{"上涨" if price_trend > 0 else "下跌"}，'
                                   f'风险系数{risk_factor}'
                        )
                        db.session.add(log)
                        
                        # 执行买入操作
                        shares_to_buy = int(amount / company.current_price)
                        if not holding:
                            holding = StockHolding(
                                user_id=ai_user.id,
                                company_id=company.id,
                                shares=0,
                                average_cost=0
                            )
                            db.session.add(holding)
                        
                        # 更新持仓
                        total_cost = holding.shares * holding.average_cost + shares_to_buy * company.current_price
                        holding.shares += shares_to_buy
                        holding.average_cost = total_cost / holding.shares
                        
                        # 扣除资金
                        ai_user.balance -= Decimal(shares_to_buy * float(company.current_price))
                        
                elif current_position > ai.max_position:  # 持仓过高，考虑卖出
                    if holding and holding.shares > 0:
                        # 根据趋势调整卖出意愿
                        if price_trend > 0.5 and ai.strategy_type == 1:  # 保守型在上涨趋势时不卖出
                            continue
                        
                        # 计算卖出数量
                        shares_to_sell = min(
                            holding.shares,
                            int(trade_volume * (1 + abs(price_trend)))  # 跌得越多卖得越多
                        )
                        
                        # 记录交易日志
                        log = AITradeLog(
                            ai_id=ai.id,
                            company_id=company.id,
                            action='sell',
                            reason=f'当前持仓{current_position:.2f}%超过最大持仓{ai.max_position}%，'
                                   f'价格趋势{"上涨" if price_trend > 0 else "下跌"}，'
                                   f'风险系数{risk_factor}'
                        )
                        db.session.add(log)
                        
                        # 执行卖出操作
                        holding.shares -= shares_to_sell
                        
                        # 增加资金
                        ai_user.balance += Decimal(shares_to_sell * float(company.current_price))
                        
                        # 如果全部卖出，删除持仓记录
                        if holding.shares == 0:
                            db.session.delete(holding)
        
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"AI交易失败: {str(e)}", exc_info=True)

@with_app_context
def generate_news():
    """新闻生成任务，每小时执行一次"""
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
                    type=3,  # 市场动态
                    company_id=company.id,
                    impact_score=min(5, int(abs(price_change) / 2)),
                    status=1
                )
                db.session.add(news)
        
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        print(f"生成新闻失败: {str(e)}")

@with_app_context
def calculate_deposit_interest():
    """计算存款利息，每天执行一次"""
    try:
        deposits = DepositAccount.query.filter_by(status=1).all()
        
        for deposit in deposits:
            # 计算日利率
            daily_rate = float(deposit.interest_rate) / 100 / 365
            
            # 计算利息
            interest = float(deposit.amount) * daily_rate
            
            # 活期存款直接加入余额
            if deposit.type == '活期':
                user = db.session.get(User, deposit.user_id)
                user.balance = float(user.balance) + interest
                
            # 定期存款到期处理
            elif deposit.end_date and deposit.end_date <= datetime.now().date():
                user = db.session.get(User, deposit.user_id)
                total_interest = float(deposit.amount) * float(deposit.interest_rate) / 100 * \
                    ((deposit.end_date - deposit.start_date).days / 365)
                
                user.balance = float(user.balance) + float(deposit.amount) + total_interest
                deposit.status = 2  # 已提前支取
        
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        print(f"计算存款利息失败: {str(e)}")

@with_app_context
def process_loan_payment():
    """处理贷款还款，每月执行一次"""
    try:
        loans = LoanAccount.query.filter_by(status=2).all()  # 已放款的贷款
        
        for loan in loans:
            user = db.session.get(User, loan.user_id)
            
            # 如果余额足够还款
            if float(user.balance) >= float(loan.monthly_payment):
                user.balance = float(user.balance) - float(loan.monthly_payment)
                loan.remaining_amount = float(loan.remaining_amount) - \
                    (float(loan.monthly_payment) - float(loan.monthly_payment) * \
                    float(loan.interest_rate) / 100 / 12)
                
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

# 初始化定时任务
def init_scheduler():
    """初始化定时任务"""
    with app.app_context():
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
        
        # 每天开盘时初始化当日价格记录
        scheduler.add_job(
            init_daily_prices,
            trigger=CronTrigger(hour=9, minute=30),
            id='init_daily_prices',
            replace_existing=True
        )
        
        # 启动调度器
        scheduler.start()

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

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
            balance=10000000.00  # 给新用户初始资金10000000.00
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
    if request.method == 'GET':
        return render_template('company/create.html')
    
    try:
        name = request.form.get('name')
        code = request.form.get('code')
        description = request.form.get('description')
        industry = request.form.get('industry')
        registered_capital = Decimal(request.form.get('registered_capital'))
        total_shares = int(request.form.get('total_shares', 0))
        
        # 验证输入
        if not all([name, code, industry, registered_capital, total_shares]):
            return render_template('company/create.html', error='请填写所有必填字段')
        
        # 验证股票代码格式
        if not re.match(r'^[A-Z0-9]{6}$', code):
            return render_template('company/create.html', error='股票代码必须是6位大写字母或数字')
        
        if registered_capital <= 0:
            return render_template('company/create.html', error='注册资本必须大于0')
        
        if total_shares <= 0:
            return render_template('company/create.html', error='总股本必须大于0')
        
        # 检查股票代码是否已存在
        if Company.query.filter_by(code=code).first():
            return render_template('company/create.html', error='股票代码已存在')
        
        # 检查用户资金是否足够
        if current_user.balance < registered_capital:
            return render_template('company/create.html', error='您的资金不足，无法创建公司')
        
        try:
            # 创建公司
            price = Decimal(str(registered_capital / total_shares))
            company = Company(
                name=name,
                code=code,
                description=description,
                industry=industry,
                registered_capital=registered_capital,
                total_shares=total_shares,
                current_price=price,
                market_value=price * total_shares,
                creator_id=current_user.id,
                status=1
            )
            db.session.add(company)
            db.session.commit()
            
            # 初始化股票价格记录
            today = datetime.now().date()
            price = StockPrice(
                company_id=company.id,
                date=today,
                open=company.current_price,
                high=company.current_price,
                low=company.current_price,
                close=company.current_price,
                volume=0
            )
            db.session.add(price)
            db.session.commit()
            
            # 扣除用户资金
            current_user.balance -= registered_capital
            
            # 创建创始人持股记录
            holding = StockHolding(
                user_id=current_user.id,
                company_id=company.id,  # 现在company.id已经可用
                shares=total_shares,
                average_cost=registered_capital / total_shares
            )
            db.session.add(holding)
            
            db.session.commit()
            flash('公司创建成功', 'success')
            return redirect(url_for('company_detail', code=code))
            
        except Exception as e:
            print(f"创建公司失败: {str(e)}")  # 添加错误日志
            db.session.rollback()
            return render_template('company/create.html', error='创建失败，请稍后重试')
    
    except Exception as e:
        print(f"创建公司参数验证失败: {str(e)}")  # 添加错误日志
        return render_template('company/create.html', error='参数验证失败，请检查输入')

# 路由：公司详情
@app.route('/company/<code>')
def company_detail(code):
    company = Company.query.filter_by(code=code).first_or_404()
    return render_template('company/detail.html', company=company)

# 路由：股票交易
@app.route('/trade/<code>', methods=['POST'])
@login_required
def trade_stock(code):
    try:
        logging.info(f"开始处理交易请求 - 用户:{current_user.username}, 股票代码:{code}")
        # 获取交易参数
        action = 'buy' if request.form.get('type') == '1' else 'sell'
        price = Decimal(request.form.get('price', '0'))
        quantity = int(request.form.get('shares', '0'))
        
        # 获取公司信息
        company = Company.query.filter_by(code=code).first()
        if not company:
            return jsonify({'success': False, 'message': '股票不存在'})
        
        # 基本验证
        if quantity <= 0:
            return jsonify({'success': False, 'message': '交易数量必须大于0'})
        if quantity % 100 != 0:
            return jsonify({'success': False, 'message': '交易数量必须是100的整数倍'})
        if price <= 0:
            return jsonify({'success': False, 'message': '交易价格必须大于0'})
            
        amount = price * quantity
        
        if action == 'buy':
            # 检查余额
            if current_user.balance < amount:
                return jsonify({'success': False, 'message': f'余额不足，需要{amount}元，当前余额{current_user.balance}元'})
            
            # 冻结资金
            current_user.balance -= amount
            
        else:  # sell
            # 检查持仓
            holding = StockHolding.query.filter_by(
                user_id=current_user.id,
                company_id=company.id
            ).first()
            
            if not holding or holding.shares < quantity:
                return jsonify({'success': False, 'message': '持仓不足'})
        
        # 创建委托订单
        order = TradeOrder(
            user_id=current_user.id,
            company_id=company.id,
            type=1 if action == 'buy' else 2,
            price=price,
            shares=quantity,
            dealt_shares=0,
            dealt_amount=0,
            status=0  # 未成交
        )
        db.session.add(order)
        db.session.commit()
        
        # 立即尝试撮合
        match_orders(company.id)
        
        return jsonify({'success': True, 'message': '委托已提交'})
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"交易失败: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': f'交易失败: {str(e)}'})

# 撤单功能
@app.route('/trade/cancel/<int:order_id>', methods=['POST'])
@login_required
def cancel_order(order_id):
    """撤销委托订单"""
    try:
        # 获取订单
        order = TradeOrder.query.filter_by(
            id=order_id,
            user_id=current_user.id  # 确保是当前用户的订单
        ).first()
        
        if not order:
            return jsonify({'success': False, 'message': '订单不存在'})
        
        # 检查订单状态
        if order.status == 2:  # 已完全成交
            return jsonify({'success': False, 'message': '订单已完全成交，无法撤销'})
        elif order.status == 3:  # 已撤单
            return jsonify({'success': False, 'message': '订单已撤单'})
        
        # 更新订单状态为已撤销
        order.status = 3
        order.cancel_time = datetime.now()
        
        # 如果是买单，退还未成交部分的冻结资金
        unfilled_amount = 0
        if order.type == 1:  # 买单
            unfilled_amount = (order.shares - order.dealt_shares) * order.price
            current_user.balance += unfilled_amount
        
        db.session.commit()
        logging.info(f"撤单成功 - 订单ID:{order_id}, 用户:{current_user.id}")
        
        return jsonify({
            'success': True,
            'message': '撤单成功',
            'data': {
                'unfilled_shares': order.shares - order.dealt_shares,
                'unfilled_amount': float(unfilled_amount)
            }
        })
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"撤单失败: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': f'撤单失败: {str(e)}'})

# 路由：交易大厅
@app.route('/market')
def market():
    # 获取所有上市公司
    stocks = Company.query.filter_by(status=1).all()
    
    # 计算涨跌幅
    for stock in stocks:
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        
        # 获取今日价格数据
        today_price = StockPrice.query.filter_by(
            company_id=stock.id,
            date=today
        ).first()
        
        # 获取昨日收盘价
        yesterday_price = StockPrice.query.filter_by(
            company_id=stock.id,
            date=yesterday
        ).first()
        
        if yesterday_price:
            stock.price_change = stock.current_price - yesterday_price.close
            stock.price_change_percent = (stock.price_change / yesterday_price.close * 100)
        else:
            stock.price_change = 0
            stock.price_change_percent = 0
            
        # 获取今日成交量
        stock.volume = today_price.volume if today_price else 0
    
    return render_template('market/index.html', stocks=stocks)

# API：获取实时行情
@app.route('/api/market/stocks')
def get_market_stocks():
    stocks = Company.query.filter_by(status=1).all()
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    
    result = []
    for stock in stocks:
        # 获取今日价格数据
        today_price = StockPrice.query.filter_by(
            company_id=stock.id,
            date=today
        ).first()
        
        # 获取昨日收盘价
        yesterday_price = StockPrice.query.filter_by(
            company_id=stock.id,
            date=yesterday
        ).first()
        
        price_change = 0
        price_change_percent = 0
        if yesterday_price:
            price_change = stock.current_price - yesterday_price.close
            price_change_percent = (price_change / yesterday_price.close * 100)
            
        result.append({
            'code': stock.code,
            'current_price': float(stock.current_price),
            'price_change': float(price_change),
            'price_change_percent': float(price_change_percent),
            'volume': today_price.volume if today_price else 0,
            'market_value': float(stock.market_value)
        })
    
    return jsonify(result)

# 路由：个人资产
@app.route('/portfolio')
@login_required
def portfolio():
    logging.debug(f"查询用户{current_user.id}的持仓信息")
    # 获取用户的持仓列表
    holdings = StockHolding.query.filter_by(user_id=current_user.id).all()
    logging.debug(f"找到{len(holdings)}条持仓记录")
    
    # 获取每个持仓的公司信息
    for holding in holdings:
        holding.company = Company.query.get(holding.company_id)
        
        # 计算持仓市值和盈亏
        holding.market_value = holding.shares * holding.company.current_price
        holding.profit = holding.market_value - (holding.shares * holding.average_cost)
        holding.profit_percent = (holding.profit / (holding.shares * holding.average_cost)) * 100
    
    # 获取最近交易记录
    orders = TradeOrder.query.filter_by(user_id=current_user.id)\
        .order_by(TradeOrder.created_at.desc())\
        .limit(20)\
        .all()
    
    # 为每个订单加载公司信息
    for order in orders:
        order.company = Company.query.get(order.company_id)
    
    # 计算总资产
    stock_value = sum(h.market_value for h in holdings)
    total_assets = current_user.balance + stock_value
    total_profit = sum(h.profit for h in holdings)
    
    logging.debug(f"用户资产统计 - 总资产:{total_assets}, 股票市值:{stock_value}, 总盈亏:{total_profit}")
    
    # 格式化订单状态
    status_map = {
        0: '未成交',
        1: '部分成交',
        2: '完全成交',
        3: '已撤单'
    }
    
    for order in orders:
        order.status_text = status_map.get(order.status, '未知')
        order.can_cancel = order.status in [0, 1]  # 只有未成交和部分成交的订单可以撤单
    
    return render_template('user/portfolio.html',
                         holdings=holdings,
                         orders=orders,
                         total_assets=total_assets,
                         stock_value=stock_value,
                         total_profit=total_profit)

# API：获取股票K线数据
@app.route('/api/stock/<code>/kline')
def get_stock_kline(code):
    """获取K线图数据"""
    try:
        company = Company.query.filter_by(code=code).first_or_404()
        
        # 获取最近30天的价格数据
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
        
        prices = StockPrice.query.filter(
            StockPrice.company_id == company.id,
            StockPrice.date >= start_date,
            StockPrice.date <= end_date
        ).order_by(StockPrice.date.asc()).all()
        
        data = [{
            'time': price.date.strftime('%Y-%m-%d'),
            'open': float(price.open),
            'high': float(price.high),
            'low': float(price.low),
            'close': float(price.close),
            'volume': price.volume
        } for price in prices]
        
        return jsonify(data)
        
    except Exception as e:
        logging.error(f"获取K线数据失败: {str(e)}", exc_info=True)
        return jsonify({'error': '获取K线数据失败'})

# 路由：AI玩家管理
@app.route('/ai')
@login_required
def ai_index():
    ai_players = AIStrategy.query.filter_by(ai_user_id=current_user.id).all()
    return render_template('ai/index.html', ai_players=ai_players)

# 路由：创建AI玩家
@app.route('/ai/create', methods=['POST'])
@login_required
def create_ai():
    try:
        # 创建AI玩家
        ai = AIStrategy(
            ai_user_id=current_user.id,
            strategy_type=int(request.form.get('strategy')),
            risk_level=int(request.form.get('risk_level')),
            min_position=int(request.form.get('min_position')),
            max_position=int(request.form.get('max_position')),
            min_price=Decimal(request.form.get('min_price')),
            max_price=Decimal(request.form.get('max_price')),
            position_limit=int(request.form.get('position_limit')),
            status=1  # 默认启用
        )
        
        db.session.add(ai)
        db.session.commit()
        
        flash('AI玩家创建成功', 'success')
        return redirect(url_for('ai_index'))
        
    except Exception as e:
        logging.error(f"创建AI玩家失败: {str(e)}", exc_info=True)
        flash('创建AI玩家失败，请重试', 'danger')
        return redirect(url_for('ai_index'))

# 路由：切换AI状态
@app.route('/ai/<int:ai_id>/toggle', methods=['POST'])
@login_required
def toggle_ai(ai_id):
    ai = AIStrategy.query.filter_by(id=ai_id, ai_user_id=current_user.id).first_or_404()
    ai.status = 1 if ai.status == 0 else 0
    db.session.commit()
    return jsonify({'success': True})

# 路由：获取AI交易日志
@app.route('/ai/<int:ai_id>/logs')
@login_required
def ai_logs(ai_id):
    ai = AIStrategy.query.filter_by(id=ai_id, ai_user_id=current_user.id).first_or_404()
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
    total_deposits = sum(d.amount for d in deposits)
    total_loans = sum(l.remaining_amount for l in loans)
    
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
        amount = Decimal(request.form.get('amount'))
        deposit_type = request.form.get('type')
        
        if amount <= 0:
            return jsonify({'success': False, 'message': '存款金额必须大于0'})
            
        if current_user.balance < amount:
            return jsonify({'success': False, 'message': '余额不足'})
        
        # 设置利率
        if deposit_type == '活期':
            interest_rate = Decimal('0.35')  # 年利率0.35%
            end_date = None
        else:  # 定期
            term = int(request.form.get('term'))  # 存期（月）
            if term == 3:
                interest_rate = Decimal('1.1')
            elif term == 6:
                interest_rate = Decimal('1.3')
            elif term == 12:
                interest_rate = Decimal('1.5')
            else:
                interest_rate = Decimal('1.7')  # 2年期
            
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
        
        # 计算利息
        interest = amount * interest_rate / Decimal('100')
        
        # 更新存款账户
        deposit.amount = deposit.amount + interest
        
        db.session.add(deposit)
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

# API：获取买卖盘口数据
@app.route('/api/stock/<code>/orderbook')
def get_stock_orderbook(code):
    try:
        company = Company.query.filter_by(code=code).first_or_404()
        
        # 获取买盘(价格降序)
        buy_orders = TradeOrder.query.filter(
            TradeOrder.company_id == company.id,
            TradeOrder.type == 1,  # 买单
            TradeOrder.status.in_([0, 1]),  # 未成交或部分成交
            TradeOrder.shares > TradeOrder.dealt_shares  # 还有未成交数量
        ).order_by(
            TradeOrder.price.desc()
        ).limit(5).all()
        
        # 获取卖盘(价格升序)
        sell_orders = TradeOrder.query.filter(
            TradeOrder.company_id == company.id,
            TradeOrder.type == 2,  # 卖单
            TradeOrder.status.in_([0, 1]),  # 未成交或部分成交
            TradeOrder.shares > TradeOrder.dealt_shares  # 还有未成交数量
        ).order_by(
            TradeOrder.price.asc()
        ).limit(5).all()
        
        # 格式化数据
        buy_list = [{
            'price': float(order.price),
            'volume': order.shares - order.dealt_shares
        } for order in buy_orders]
        
        sell_list = [{
            'price': float(order.price),
            'volume': order.shares - order.dealt_shares
        } for order in sell_orders]
        
        return jsonify({
            'buy': buy_list,
            'sell': sell_list
        })
        
    except Exception as e:
        logging.error(f"获取盘口数据失败: {str(e)}", exc_info=True)
        return jsonify({'error': '获取盘口数据失败'})

# API：获取分时成交数据
@app.route('/api/stock/<code>/trades')
def get_stock_trades(code):
    try:
        company = Company.query.filter_by(code=code).first_or_404()
        today = datetime.now().date()
        
        # 获取今日成交记录
        trades = TradeRecord.query.filter(
            TradeRecord.company_id == company.id,
            func.date(TradeRecord.created_at) == today
        ).order_by(
            TradeRecord.created_at.desc()
        ).limit(20).all()
        
        return jsonify([{
            'time': trade.created_at.strftime('%H:%M:%S'),
            'price': float(trade.price),
            'volume': trade.shares,
            'amount': float(trade.amount)
        } for trade in trades])
        
    except Exception as e:
        logging.error(f"获取分时成交数据失败: {str(e)}", exc_info=True)
        return jsonify({'error': '获取分时成交数据失败'})

# 在应用启动时初始化定时任务
if __name__ == '__main__':
    init_scheduler()
    app.run(host='0.0.0.0', port=5010, debug=True) 