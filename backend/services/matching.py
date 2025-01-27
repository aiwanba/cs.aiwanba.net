from models import Order, Stock, StockTransaction
from app import db
from decimal import Decimal
from services.websocket import WebSocketService

class MatchingEngine:
    @staticmethod
    def create_order(company_id, user_id, order_type, amount, price):
        """创建订单"""
        # 验证用户资格
        if order_type == 'sell':
            stock = Stock.query.filter_by(
                company_id=company_id,
                holder_id=user_id,
                is_frozen=False
            ).first()
            if not stock or stock.amount < amount:
                raise ValueError("持仓不足")
        else:  # buy
            user = User.query.get(user_id)
            if user.balance < Decimal(str(price)) * Decimal(str(amount)):
                raise ValueError("余额不足")
                
        # 创建订单
        order = Order(
            company_id=company_id,
            user_id=user_id,
            order_type=order_type,
            amount=amount,
            price=price,
            status='pending'
        )
        
        # 如果是卖单，冻结股票
        if order_type == 'sell':
            stock.amount -= amount
            frozen_stock = Stock(
                company_id=company_id,
                holder_id=user_id,
                amount=amount,
                is_frozen=True
            )
            db.session.add(frozen_stock)
            
        db.session.add(order)
        db.session.commit()
        
        # 尝试撮合
        MatchingEngine.try_match(company_id)
        
        return order
        
    @staticmethod
    def try_match(company_id):
        """尝试撮合订单"""
        # 获取所有待成交订单，按价格排序
        buy_orders = Order.query.filter_by(
            company_id=company_id,
            order_type='buy',
            status='pending'
        ).order_by(Order.price.desc()).all()
        
        sell_orders = Order.query.filter_by(
            company_id=company_id,
            order_type='sell',
            status='pending'
        ).order_by(Order.price.asc()).all()
        
        for buy_order in buy_orders:
            for sell_order in sell_orders:
                # 如果买价大于等于卖价，可以撮合
                if buy_order.price >= sell_order.price:
                    # 确定成交价格（取中间价）
                    trade_price = (buy_order.price + sell_order.price) / 2
                    # 确定成交数量（取较小值）
                    trade_amount = min(buy_order.amount, sell_order.amount)
                    
                    # 执行交易
                    try:
                        MatchingEngine.execute_trade(
                            company_id=company_id,
                            buy_order=buy_order,
                            sell_order=sell_order,
                            amount=trade_amount,
                            price=trade_price
                        )
                    except Exception as e:
                        print(f"交易执行失败: {str(e)}")
                        continue
                        
                    # 更新订单状态
                    if buy_order.amount == trade_amount:
                        buy_order.status = 'filled'
                    if sell_order.amount == trade_amount:
                        sell_order.status = 'filled'
                        
                    db.session.commit()
                    
    @staticmethod
    def execute_trade(company_id, buy_order, sell_order, amount, price):
        """执行撮合的交易"""
        try:
            # 计算交易金额
            trade_amount = Decimal(str(price)) * Decimal(str(amount))
            
            # 更新买家余额
            buyer = User.query.get(buy_order.user_id)
            buyer.balance -= trade_amount
            
            # 更新卖家余额
            seller = User.query.get(sell_order.user_id)
            seller.balance += trade_amount
            
            # 更新买家持仓
            buyer_stock = Stock.query.filter_by(
                company_id=company_id,
                holder_id=buyer.id,
                is_frozen=False
            ).first()
            
            if buyer_stock:
                buyer_stock.amount += amount
            else:
                buyer_stock = Stock(
                    company_id=company_id,
                    holder_id=buyer.id,
                    amount=amount,
                    is_frozen=False
                )
                db.session.add(buyer_stock)
                
            # 更新卖家冻结股票
            frozen_stock = Stock.query.filter_by(
                company_id=company_id,
                holder_id=seller.id,
                is_frozen=True
            ).first()
            
            frozen_stock.amount -= amount
            if frozen_stock.amount == 0:
                db.session.delete(frozen_stock)
                
            # 记录交易
            transaction = StockTransaction(
                company_id=company_id,
                seller_id=seller.id,
                buyer_id=buyer.id,
                amount=amount,
                price=price
            )
            db.session.add(transaction)
            
            # 更新公司股价
            company = Company.query.get(company_id)
            company.current_price = price
            
            # 广播更新
            WebSocketService.broadcast_stock_price(company_id, price)
            WebSocketService.broadcast_transaction({
                'company_id': company_id,
                'amount': amount,
                'price': float(price),
                'time': transaction.created_at.isoformat()
            })
            
            db.session.commit()
            return transaction
            
        except Exception as e:
            db.session.rollback()
            raise e 