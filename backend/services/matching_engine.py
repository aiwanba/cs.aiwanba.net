from models import Order, Stock, Company, StockTransaction
from extensions import db
from decimal import Decimal
from flask import current_app

class MatchingEngine:
    @staticmethod
    def try_match(company_id):
        """尝试撮合交易"""
        try:
            # 获取所有待处理的买单，按价格降序排列（价高者优先）
            buy_orders = Order.query.filter_by(
                company_id=company_id,
                order_type='buy',
                status='pending'
            ).order_by(Order.price.desc()).all()
            
            # 获取所有待处理的卖单，按价格升序排列（价低者优先）
            sell_orders = Order.query.filter_by(
                company_id=company_id,
                order_type='sell',
                status='pending'
            ).order_by(Order.price.asc()).all()
            
            for buy_order in buy_orders:
                for sell_order in sell_orders:
                    # 如果买入价大于等于卖出价，可以撮合
                    if buy_order.price >= sell_order.price:
                        # 确定成交数量
                        trade_amount = min(buy_order.amount, sell_order.amount)
                        # 以卖方价格成交
                        trade_price = sell_order.price
                        
                        # 创建交易记录
                        transaction = StockTransaction(
                            company_id=company_id,
                            seller_id=sell_order.user_id,
                            buyer_id=buy_order.user_id,
                            amount=trade_amount,
                            price=trade_price
                        )
                        
                        # 更新买方持仓
                        buyer_stock = Stock.query.filter_by(
                            company_id=company_id,
                            holder_id=buy_order.user_id,
                            is_frozen=False
                        ).first()
                        
                        if not buyer_stock:
                            buyer_stock = Stock(
                                company_id=company_id,
                                holder_id=buy_order.user_id,
                                amount=0,
                                is_frozen=False
                            )
                            db.session.add(buyer_stock)
                            
                        buyer_stock.amount += trade_amount
                        
                        # 更新卖方持仓
                        seller_stock = Stock.query.filter_by(
                            company_id=company_id,
                            holder_id=sell_order.user_id,
                            is_frozen=True
                        ).first()
                        
                        if seller_stock:
                            seller_stock.amount -= trade_amount
                            if seller_stock.amount == 0:
                                db.session.delete(seller_stock)
                                
                        # 更新订单状态
                        if trade_amount == buy_order.amount:
                            buy_order.status = 'completed'
                        else:
                            buy_order.amount -= trade_amount
                            
                        if trade_amount == sell_order.amount:
                            sell_order.status = 'completed'
                        else:
                            sell_order.amount -= trade_amount
                            
                        # 更新公司股价
                        company = Company.query.get(company_id)
                        company.current_price = trade_price
                        
                        db.session.add(transaction)
                        db.session.commit()
                        
                        # 如果买单已完成，跳出内层循环
                        if buy_order.status == 'completed':
                            break
                            
                # 如果买单已完成，继续下一个买单
                if buy_order.status == 'completed':
                    continue
                    
        except Exception as e:
            current_app.logger.error(f"撮合交易失败: {str(e)}")
            db.session.rollback()
            raise e 