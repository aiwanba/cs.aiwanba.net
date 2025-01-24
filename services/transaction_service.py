from models import db
from models.transaction import Transaction, Order
from models.stock import Stock
from models.company import Company
from models.bank import BankAccount
from services.bank_service import BankService
from datetime import datetime

class TransactionService:
    """交易服务"""
    
    @staticmethod
    def create_market_order(company_id, stock_id, order_type, shares, price):
        """创建市价单"""
        # 检查公司账户余额
        account = BankAccount.query.filter_by(company_id=company_id).first()
        if not account:
            raise Exception("公司账户不存在")
            
        total_amount = shares * price
        if account.balance < total_amount:
            raise Exception("账户余额不足")
            
        # 创建订单
        order = Order(
            company_id=company_id,
            order_type=order_type,
            stock_id=stock_id,
            shares=shares,
            price=price,
            status='pending'
        )
        db.session.add(order)
        db.session.commit()
        return order
    
    @staticmethod
    def execute_order(order_id):
        """执行订单"""
        order = Order.query.get(order_id)
        if not order:
            raise Exception("订单不存在")
            
        # 执行交易逻辑
        # ...
        
        # 更新订单状态
        order.status = 'completed'
        db.session.commit()
        return order
    
    @staticmethod
    def get_transaction_history(company_id):
        """获取交易历史"""
        transactions = Transaction.query.filter(
            (Transaction.buyer_company_id == company_id) |
            (Transaction.seller_company_id == company_id)
        ).order_by(Transaction.created_at.desc()).all()
        
        return transactions
    
    @staticmethod
    def create_limit_order(company_id, stock_id, shares, price, is_buy):
        """
        创建限价单
        :param company_id: 交易发起公司ID
        :param stock_id: 股票ID
        :param shares: 股数
        :param price: 限价
        :param is_buy: 是否买入
        """
        order = Order(
            company_id=company_id,
            order_type='buy' if is_buy else 'sell',
            stock_id=stock_id,
            shares=shares,
            price=price,
            status='pending'
        )
        
        db.session.add(order)
        db.session.commit()
        
        # 尝试撮合订单
        TransactionService.match_orders(stock_id)
        
        return order
    
    @staticmethod
    def match_orders(stock_id):
        """
        撮合订单
        :param stock_id: 股票ID
        """
        # 获取所有未完成的买单和卖单
        buy_orders = Order.query.filter_by(
            stock_id=stock_id,
            order_type='buy',
            status='pending'
        ).order_by(Order.price.desc()).all()
        
        sell_orders = Order.query.filter_by(
            stock_id=stock_id,
            order_type='sell',
            status='pending'
        ).order_by(Order.price.asc()).all()
        
        for buy_order in buy_orders:
            for sell_order in sell_orders:
                # 如果买单价格大于等于卖单价格，可以撮合
                if buy_order.price >= sell_order.price:
                    # 确定成交价格（取中间价）
                    deal_price = (buy_order.price + sell_order.price) / 2
                    # 确定成交数量（取较小值）
                    deal_shares = min(buy_order.shares, sell_order.shares)
                    
                    try:
                        # 创建交易记录
                        transaction = Transaction(
                            buyer_company_id=buy_order.company_id,
                            seller_company_id=sell_order.company_id,
                            stock_id=stock_id,
                            shares=deal_shares,
                            price=deal_price,
                            total_amount=deal_price * deal_shares,
                            order_type='limit',
                            status='completed',
                            completed_at=datetime.utcnow()
                        )
                        
                        # 更新订单状态
                        buy_order.shares -= deal_shares
                        sell_order.shares -= deal_shares
                        
                        if buy_order.shares == 0:
                            buy_order.status = 'completed'
                        if sell_order.shares == 0:
                            sell_order.status = 'completed'
                        
                        db.session.add(transaction)
                        db.session.commit()
                        
                    except Exception as e:
                        db.session.rollback()
                        raise e 