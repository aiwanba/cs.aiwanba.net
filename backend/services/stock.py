from models import Stock, StockTransaction, Company, User
from extensions import db
from decimal import Decimal
from sqlalchemy import and_
from services.websocket import WebSocketService

class StockService:
    @staticmethod
    def create_order(company_id, seller_id, amount, price):
        """创建卖单"""
        # 检查持仓
        stock = Stock.query.filter_by(
            company_id=company_id,
            holder_id=seller_id,
            is_frozen=False
        ).first()
        
        if not stock or stock.amount < amount:
            raise ValueError("持仓不足")
            
        # 冻结股票
        stock.amount -= amount
        new_frozen_stock = Stock(
            company_id=company_id,
            holder_id=seller_id,
            amount=amount,
            is_frozen=True
        )
        
        db.session.add(new_frozen_stock)
        db.session.commit()
        
        return {
            'order_id': new_frozen_stock.id,
            'amount': amount,
            'price': float(price)
        }
        
    @staticmethod
    def execute_trade(company_id, seller_id, buyer_id, amount, price):
        """执行交易"""
        try:
            # 查找冻结的股票
            frozen_stock = Stock.query.filter(and_(
                Stock.company_id == company_id,
                Stock.holder_id == seller_id,
                Stock.is_frozen == True,
                Stock.amount >= amount
            )).first()
            
            if not frozen_stock:
                raise ValueError("未找到对应的冻结股票")
                
            # 计算交易金额
            trade_amount = Decimal(str(price)) * Decimal(str(amount))
            
            # 检查买家余额
            buyer = User.query.get(buyer_id)
            if buyer.balance < trade_amount:
                raise ValueError("买家余额不足")
                
            # 更新买家余额
            buyer.balance -= trade_amount
            
            # 更新卖家余额
            seller = User.query.get(seller_id)
            seller.balance += trade_amount
            
            # 更新股票持有
            frozen_stock.amount -= amount
            if frozen_stock.amount == 0:
                db.session.delete(frozen_stock)
                
            # 查找或创建买家的持仓记录
            buyer_stock = Stock.query.filter_by(
                company_id=company_id,
                holder_id=buyer_id,
                is_frozen=False
            ).first()
            
            if buyer_stock:
                buyer_stock.amount += amount
            else:
                buyer_stock = Stock(
                    company_id=company_id,
                    holder_id=buyer_id,
                    amount=amount,
                    is_frozen=False
                )
                db.session.add(buyer_stock)
                
            # 记录交易
            transaction = StockTransaction(
                company_id=company_id,
                seller_id=seller_id,
                buyer_id=buyer_id,
                amount=amount,
                price=price
            )
            db.session.add(transaction)
            
            # 更新公司当前股价
            company = Company.query.get(company_id)
            company.current_price = price
            
            # 广播价格更新
            WebSocketService.broadcast_stock_price(company_id, price)
            
            # 广播交易信息
            transaction_data = {
                'company_id': company_id,
                'amount': amount,
                'price': float(price),
                'time': transaction.created_at.isoformat()
            }
            WebSocketService.broadcast_transaction(transaction_data)
            
            db.session.commit()
            return transaction
            
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def create_transaction(seller_id, buyer_id, company_id, amount, price):
        """创建交易记录"""
        try:
            # 验证卖家
            seller = User.query.get(seller_id)
            if not seller:
                raise ValueError('卖家不存在')
                
            # 验证买家
            buyer = User.query.get(buyer_id)
            if not buyer:
                raise ValueError('买家不存在')
            
            # 创建交易记录
            transaction = StockTransaction(
                company_id=company_id,
                seller_id=seller_id,
                buyer_id=buyer_id,
                amount=amount,
                price=price
            )
            
            db.session.add(transaction)
            db.session.commit()
            
            return transaction
            
        except Exception as e:
            db.session.rollback()
            raise e 