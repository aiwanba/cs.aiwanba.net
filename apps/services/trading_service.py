from apps.models.transaction import Transaction
from apps.models.stock import StockHolding
from app import db

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
        
        # 更新用户持股
        holding = StockHolding.query.filter_by(
            holder_id=user.id,
            company_id=company.id
        ).first()
        
        if holding:
            holding.shares += shares
            # 更新平均购买价格
            total_cost = (float(holding.purchase_price) * (holding.shares - shares) + 
                         float(price) * shares)
            holding.purchase_price = total_cost / holding.shares
        else:
            holding = StockHolding(
                holder_id=user.id,
                company_id=company.id,
                shares=shares,
                purchase_price=price
            )
            db.session.add(holding)
        
        # 更新用户余额和公司可用股数
        user.balance -= total_amount
        company.available_shares -= shares
        
        db.session.add(transaction)
        db.session.commit()
        
        return True, "交易成功"

    @staticmethod
    def sell_stock(user, company, shares, price):
        """卖出股票"""
        # 检查用户持股
        holding = StockHolding.query.filter_by(
            holder_id=user.id,
            company_id=company.id
        ).first()
        
        if not holding or holding.shares < shares:
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
        
        # 更新持股记录
        holding.shares -= shares
        if holding.shares == 0:
            db.session.delete(holding)
        
        # 更新用户余额和公司可用股数
        user.balance += total_amount
        company.available_shares += shares
        
        db.session.add(transaction)
        db.session.commit()
        
        return True, "交易成功"
    
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