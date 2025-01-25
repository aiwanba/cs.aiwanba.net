from apps.models.transaction import Transaction
from apps.models.stock import StockHolding
from apps.extensions import db

class TradingService:
    @staticmethod
    def buy_stock(user, company, shares, price):
        """购买股票"""
        total_amount = shares * price
        
        # 检查用户余额
        if float(user.balance) < total_amount:
            return False, "余额不足"
        
        # 检查可用股数
        if company.available_shares < shares:
            return False, "可用股数不足"
        
        # 创建交易记录
        transaction = Transaction(
            user_id=user.id,
            company_id=company.id,
            type='buy',
            shares=shares,
            price=price,
            total_amount=total_amount
        )
        
        # 更新用户余额
        user.balance -= total_amount
        
        # 更新公司可用股数
        company.available_shares -= shares
        
        # 更新或创建持股记录
        stock = StockHolding.query.filter_by(
            holder_id=user.id,
            company_id=company.id
        ).first()
        
        if stock:
            # 更新现有持股
            stock.shares += shares
            # 更新平均购买价格
            stock.purchase_price = (float(stock.purchase_price) * stock.shares + total_amount) / (stock.shares + shares)
        else:
            # 创建新持股记录
            stock = StockHolding(
                holder_id=user.id,
                company_id=company.id,
                shares=shares,
                purchase_price=price
            )
            db.session.add(stock)
        
        db.session.add(transaction)
        db.session.commit()
        
        return True, transaction
    
    @staticmethod
    def sell_stock(user, company, shares, price):
        """出售股票"""
        # 检查持股记录
        stock = StockHolding.query.filter_by(
            holder_id=user.id,
            company_id=company.id
        ).first()
        
        if not stock or stock.shares < shares:
            return False, "持股数量不足"
        
        total_amount = shares * price
        
        # 创建交易记录
        transaction = Transaction(
            user_id=user.id,
            company_id=company.id,
            type='sell',
            shares=shares,
            price=price,
            total_amount=total_amount
        )
        
        # 更新用户余额
        user.balance += total_amount
        
        # 更新公司可用股数
        company.available_shares += shares
        
        # 更新持股记录
        stock.shares -= shares
        if stock.shares == 0:
            db.session.delete(stock)
        
        db.session.add(transaction)
        db.session.commit()
        
        return True, transaction
    
    @staticmethod
    def get_user_holdings(user_id):
        """获取用户持仓"""
        holdings = StockHolding.query.filter_by(holder_id=user_id).all()
        return [{
            'company_name': holding.company.name,
            'shares': holding.shares,
            'purchase_price': float(holding.purchase_price),
            'current_price': float(holding.company.current_price),
            'current_value': holding.current_value(),
            'profit_loss': holding.profit_loss()
        } for holding in holdings]
    
    @staticmethod
    def get_transaction_history(user_id=None, company_id=None):
        """获取交易历史"""
        query = Transaction.query
        
        if user_id:
            query = query.filter_by(user_id=user_id)
        if company_id:
            query = query.filter_by(company_id=company_id)
            
        transactions = query.order_by(Transaction.created_at.desc()).all()
        
        return [{
            'id': t.id,
            'type': t.type,
            'company_name': t.company.name,
            'shares': t.shares,
            'price': float(t.price),
            'total_amount': float(t.total_amount),
            'created_at': t.created_at.strftime('%Y-%m-%d %H:%M:%S')
        } for t in transactions] 