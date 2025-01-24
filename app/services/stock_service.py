from app import db
from app.models.stock import Stock, Transaction
from app.models.company import Company
from app.models.user import User
from app.utils.exceptions import StockError
from flask_socketio import emit
from sqlalchemy import func
import redis
import json

class StockService:
    def __init__(self):
        self.redis_client = redis.from_url('redis://localhost:6379/0')
    
    def buy_stock(self, company_id, user_id, quantity):
        """购买股票"""
        if quantity <= 0:
            raise StockError("Quantity must be positive")
            
        company = Company.query.get(company_id)
        if not company:
            raise StockError("Company not found", 404)
            
        user = User.query.get(user_id)
        if not user:
            raise StockError("User not found", 404)
            
        total_cost = company.current_price * quantity
        if user.balance < total_cost:
            raise StockError("Insufficient funds")
            
        try:
            # 更新用户余额
            user.update_balance(-total_cost)
            
            # 查找或创建股票持仓记录
            stock = Stock.query.filter_by(
                company_id=company_id,
                owner_id=user_id
            ).first()
            
            if stock:
                # 更新现有持仓
                stock.update_quantity(quantity)
            else:
                # 创建新持仓
                stock = Stock(
                    company_id=company_id,
                    owner_id=user_id,
                    quantity=quantity,
                    purchase_price=company.current_price
                )
                db.session.add(stock)
            
            # 创建交易记录
            transaction = Transaction(
                company_id=company_id,
                user_id=user_id,
                type='buy',
                quantity=quantity,
                price=company.current_price
            )
            db.session.add(transaction)
            db.session.commit()
            
            # 发送WebSocket通知
            emit('stock_transaction', {
                'type': 'buy',
                'company_id': company_id,
                'quantity': quantity,
                'price': company.current_price
            }, broadcast=True)
            
            # 更新Redis缓存的市场数据
            self._update_market_data(company_id)
            
            return transaction
            
        except Exception as e:
            db.session.rollback()
            raise StockError(str(e))
    
    def sell_stock(self, company_id, user_id, quantity):
        """卖出股票"""
        if quantity <= 0:
            raise StockError("Quantity must be positive")
            
        stock = Stock.query.filter_by(
            company_id=company_id,
            owner_id=user_id
        ).first()
        
        if not stock or stock.quantity < quantity:
            raise StockError("Insufficient stock quantity")
            
        company = Company.query.get(company_id)
        user = User.query.get(user_id)
        
        try:
            # 计算卖出收入
            total_income = company.current_price * quantity
            
            # 更新用户余额
            user.update_balance(total_income)
            
            # 更新股票持仓
            stock.update_quantity(-quantity)
            
            # 创建交易记录
            transaction = Transaction(
                company_id=company_id,
                user_id=user_id,
                type='sell',
                quantity=quantity,
                price=company.current_price
            )
            db.session.add(transaction)
            db.session.commit()
            
            # 发送WebSocket通知
            emit('stock_transaction', {
                'type': 'sell',
                'company_id': company_id,
                'quantity': quantity,
                'price': company.current_price
            }, broadcast=True)
            
            # 更新Redis缓存的市场数据
            self._update_market_data(company_id)
            
            return transaction
            
        except Exception as e:
            db.session.rollback()
            raise StockError(str(e))
    
    def get_user_portfolio(self, user_id):
        """获取用户投资组合"""
        stocks = Stock.query.filter_by(owner_id=user_id).all()
        return {
            'stocks': [stock.to_dict() for stock in stocks],
            'total_value': sum(stock.calculate_value() for stock in stocks)
        }
    
    def get_user_transactions(self, user_id, page=1, per_page=10):
        """获取用户交易历史"""
        return Transaction.query.filter_by(user_id=user_id)\
            .order_by(Transaction.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
    
    def get_market_data(self):
        """获取市场数据"""
        # 先尝试从Redis获取缓存的市场数据
        market_data = self.redis_client.get('market_data')
        if market_data:
            return json.loads(market_data)
            
        # 如果没有缓存，则从数据库查询
        data = {
            'total_transactions': Transaction.query.count(),
            'total_volume': db.session.query(func.sum(Transaction.quantity)).scalar() or 0,
            'active_companies': Company.query.count(),
            'latest_transactions': [
                t.to_dict() for t in 
                Transaction.query.order_by(Transaction.created_at.desc()).limit(10)
            ]
        }
        
        # 缓存市场数据（30秒）
        self.redis_client.setex('market_data', 30, json.dumps(data))
        return data
    
    def _update_market_data(self, company_id):
        """更新市场数据缓存"""
        self.redis_client.delete('market_data')
        # 市场数据将在下次请求时重新生成 