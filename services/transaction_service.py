from app import db
from models.transaction import Transaction, Order
from models.stock import Stock
from models.company import Company
from services.bank_service import BankService
from datetime import datetime

class TransactionService:
    """交易服务"""
    
    @staticmethod
    def create_market_order(company_id, stock_id, shares, is_buy):
        """
        创建市价单
        :param company_id: 交易发起公司ID
        :param stock_id: 股票ID
        :param shares: 股数
        :param is_buy: 是否买入
        """
        stock = Stock.query.get(stock_id)
        company = Company.query.get(company_id)
        
        if not all([stock, company]):
            raise ValueError("股票或公司不存在")
            
        # 获取当前市场价格
        current_price = stock.current_price
        total_amount = current_price * shares
        
        # 检查买方余额或卖方持股数量
        if is_buy:
            # 检查买方余额
            buyer_account = BankAccount.query.filter_by(company_id=company_id).first()
            if not buyer_account or buyer_account.balance < total_amount:
                raise ValueError("余额不足")
            
            # 创建交易记录
            transaction = Transaction(
                buyer_company_id=company_id,
                seller_company_id=stock.company_id,
                stock_id=stock_id,
                shares=shares,
                price=current_price,
                total_amount=total_amount,
                order_type='market',
                status='completed'
            )
        else:
            # 检查卖方持股数量
            seller_stock = Stock.query.filter_by(
                company_id=company_id,
                stock_id=stock_id
            ).first()
            if not seller_stock or seller_stock.shares < shares:
                raise ValueError("持股数量不足")
            
            # 创建交易记录
            transaction = Transaction(
                seller_company_id=company_id,
                buyer_company_id=stock.company_id,
                stock_id=stock_id,
                shares=shares,
                price=current_price,
                total_amount=total_amount,
                order_type='market',
                status='completed'
            )
        
        try:
            # 执行资金转移
            if is_buy:
                BankService.transfer(
                    from_account_id=buyer_account.id,
                    to_account_id=stock.company.bank_account.id,
                    amount=total_amount,
                    description=f"购买股票 {stock.id} {shares}股"
                )
            else:
                BankService.transfer(
                    from_account_id=stock.company.bank_account.id,
                    to_account_id=company.bank_account.id,
                    amount=total_amount,
                    description=f"出售股票 {stock.id} {shares}股"
                )
            
            # 更新股票持有记录
            if is_buy:
                buyer_stock = Stock.query.filter_by(
                    company_id=company_id,
                    stock_id=stock_id
                ).first()
                if buyer_stock:
                    buyer_stock.shares += shares
                else:
                    buyer_stock = Stock(
                        company_id=company_id,
                        stock_id=stock_id,
                        shares=shares
                    )
                    db.session.add(buyer_stock)
                
                seller_stock = Stock.query.filter_by(
                    company_id=stock.company_id,
                    stock_id=stock_id
                ).first()
                seller_stock.shares -= shares
            else:
                seller_stock.shares -= shares
                buyer_stock = Stock.query.filter_by(
                    company_id=stock.company_id,
                    stock_id=stock_id
                ).first()
                buyer_stock.shares += shares
            
            transaction.completed_at = datetime.utcnow()
            db.session.add(transaction)
            db.session.commit()
            
            return transaction
            
        except Exception as e:
            db.session.rollback()
            raise e
    
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