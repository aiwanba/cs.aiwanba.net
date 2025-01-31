from datetime import datetime
from decimal import Decimal
from app import db
from app.models.trade import Order, Trade, Shareholding
from app.models.company import Company
from app.models.message import Message
from flask import current_app

class TradeService:
    @staticmethod
    def create_order(company_id, user_id, order_type, price_type, price, quantity):
        """创建交易订单"""
        company = Company.query.get(company_id)
        if not company:
            return False, "公司不存在"
        
        if company.status != 1:
            return False, "公司股票已停牌或已退市"
        
        # 检查交易数量
        if quantity < 100:
            return False, "交易数量必须大于等于100股"
        if quantity % 100 != 0:
            return False, "交易数量必须是100的整数倍"
        
        try:
            # 创建订单
            order = Order(
                company_id=company_id,
                user_id=user_id,
                order_type=order_type,
                price_type=price_type,
                price=price,
                quantity=quantity
            )
            db.session.add(order)
            
            # 如果是卖单，检查持仓
            if order_type == 2:  # 卖出
                shareholding = Shareholding.query.filter_by(
                    company_id=company_id,
                    user_id=user_id
                ).first()
                if not shareholding or not shareholding.can_sell(quantity):
                    return False, "可售股份不足"
            
            db.session.commit()
            
            # 尝试撮合交易
            TradeService.match_orders(company_id)
            
            return True, order
        except Exception as e:
            db.session.rollback()
            return False, str(e)
    
    @staticmethod
    def match_orders(company_id):
        """撮合交易"""
        try:
            # 获取未成交的买单和卖单
            buy_orders = Order.query.filter_by(
                company_id=company_id,
                order_type=1,  # 买入
                status=1  # 未成交
            ).order_by(Order.price.desc(), Order.created_at.asc()).all()
            
            sell_orders = Order.query.filter_by(
                company_id=company_id,
                order_type=2,  # 卖出
                status=1  # 未成交
            ).order_by(Order.price.asc(), Order.created_at.asc()).all()
            
            for buy_order in buy_orders:
                for sell_order in sell_orders:
                    # 检查价格是否匹配
                    if buy_order.price_type == 1 or sell_order.price_type == 1 or \
                       buy_order.price >= sell_order.price:
                        # 计算成交数量
                        trade_quantity = min(
                            buy_order.quantity - buy_order.filled_quantity,
                            sell_order.quantity - sell_order.filled_quantity
                        )
                        
                        if trade_quantity > 0:
                            # 创建成交记录
                            trade = Trade(
                                company_id=company_id,
                                buy_order_id=buy_order.id,
                                sell_order_id=sell_order.id,
                                price=sell_order.price,
                                quantity=trade_quantity
                            )
                            db.session.add(trade)
                            
                            # 更新订单状态
                            buy_order.update_filled(trade_quantity)
                            sell_order.update_filled(trade_quantity)
                            
                            # 更新持仓
                            TradeService.update_shareholding(trade)
                            
                            # 更新公司股价
                            company = Company.query.get(company_id)
                            company.update_price(sell_order.price)
                            
                            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"撮合交易失败: {str(e)}")
            raise e
    
    @staticmethod
    def update_shareholding(trade):
        """更新持仓"""
        # 更新买方持仓
        buy_holding = Shareholding.query.filter_by(
            company_id=trade.company_id,
            user_id=trade.buy_order.user_id
        ).first()
        
        if buy_holding:
            buy_holding.update_shares(trade.quantity, trade.price)
        else:
            buy_holding = Shareholding(
                company_id=trade.company_id,
                user_id=trade.buy_order.user_id,
                shares=trade.quantity,
                cost_price=trade.price
            )
            db.session.add(buy_holding)
        
        # 更新卖方持仓
        sell_holding = Shareholding.query.filter_by(
            company_id=trade.company_id,
            user_id=trade.sell_order.user_id
        ).first()
        sell_holding.update_shares(-trade.quantity, trade.price)
    
    @staticmethod
    def cancel_order(order_id, user_id):
        """撤销订单"""
        order = Order.query.get(order_id)
        if not order:
            return False, "订单不存在"
        
        if order.user_id != user_id:
            return False, "无权操作此订单"
        
        if not order.can_cancel():
            return False, "订单状态不允许撤销"
        
        try:
            order.cancel()
            return True, order
        except Exception as e:
            db.session.rollback()
            return False, str(e)
    
    @staticmethod
    def get_order_list(user_id=None, company_id=None, status=None, page=1, per_page=10):
        """获取订单列表"""
        query = Order.query
        
        if user_id:
            query = query.filter_by(user_id=user_id)
        if company_id:
            query = query.filter_by(company_id=company_id)
        if status:
            query = query.filter_by(status=status)
        
        orders = query.order_by(Order.created_at.desc())\
                     .paginate(page=page, per_page=per_page, error_out=False)
        
        return {
            'items': [order.to_dict() for order in orders.items],
            'total': orders.total,
            'pages': orders.pages,
            'current_page': orders.page
        }
    
    @staticmethod
    def get_trade_list(company_id=None, page=1, per_page=10):
        """获取成交记录"""
        query = Trade.query
        
        if company_id:
            query = query.filter_by(company_id=company_id)
        
        trades = query.order_by(Trade.created_at.desc())\
                     .paginate(page=page, per_page=per_page, error_out=False)
        
        return {
            'items': [trade.to_dict() for trade in trades.items],
            'total': trades.total,
            'pages': trades.pages,
            'current_page': trades.page
        } 