from app.models.transaction import Transaction
from app.models.user import User
from app import db
from decimal import Decimal

class TransactionService:
    @staticmethod
    def create_transaction(user_id, type, amount, related_id=None, description=None):
        """创建资金流水"""
        try:
            # 获取用户
            user = User.query.get(user_id)
            if not user:
                return False, "用户不存在"
            
            # 计算新余额
            amount = Decimal(str(amount))
            new_balance = user.cash + amount
            
            # 创建流水记录
            transaction = Transaction(
                user_id=user_id,
                type=type,
                amount=amount,
                balance=new_balance,
                related_id=related_id,
                description=description
            )
            
            # 更新用户余额
            user.cash = new_balance
            
            db.session.add(transaction)
            db.session.commit()
            
            return True, transaction
        except Exception as e:
            db.session.rollback()
            return False, str(e) 