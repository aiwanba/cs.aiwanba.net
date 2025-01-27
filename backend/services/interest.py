from models import BankAccount, BankTransaction
from app import db
from decimal import Decimal
from datetime import datetime, timedelta
from services.websocket import WebSocketService

class InterestService:
    @staticmethod
    def calculate_daily_interest(account):
        """计算日利息"""
        if account.account_type == 'savings':
            # 储蓄年利率转日利率
            daily_rate = account.interest_rate / 365
            interest = account.balance * Decimal(str(daily_rate))
            return interest
        elif account.account_type == 'loan':
            # 贷款年利率转日利率
            daily_rate = account.interest_rate / 365
            interest = account.balance * Decimal(str(daily_rate))
            return interest
        return Decimal('0')
        
    @staticmethod
    def process_daily_interest():
        """处理每日利息"""
        accounts = BankAccount.query.all()
        
        for account in accounts:
            interest = InterestService.calculate_daily_interest(account)
            
            if interest == 0:
                continue
                
            if account.account_type == 'savings':
                # 存款加息
                account.balance += interest
                transaction_type = 'interest_earned'
            else:  # loan
                # 贷款扣息
                account.balance += interest
                transaction_type = 'interest_charged'
                
            # 记录利息交易
            transaction = BankTransaction(
                account_id=account.id,
                transaction_type=transaction_type,
                amount=interest
            )
            
            db.session.add(transaction)
            
            # 更新银行总资产
            bank = account.bank
            if account.account_type == 'savings':
                bank.total_assets -= interest
            else:  # loan
                bank.total_assets += interest
                
            # 广播利息更新
            WebSocketService.broadcast_bank_update(
                bank.id,
                'interest',
                {
                    'account_id': account.id,
                    'type': transaction_type,
                    'amount': float(interest),
                    'balance': float(account.balance)
                }
            )
            
        db.session.commit()
        
    @staticmethod
    def adjust_interest_rate(bank_id, account_type, new_rate):
        """调整利率"""
        if not (0 <= new_rate <= 1):
            raise ValueError("利率必须在0-100%之间")
            
        accounts = BankAccount.query.filter_by(
            bank_id=bank_id,
            account_type=account_type
        ).all()
        
        for account in accounts:
            old_rate = account.interest_rate
            account.interest_rate = new_rate
            
            # 广播利率调整
            WebSocketService.broadcast_bank_update(
                bank_id,
                'rate_change',
                {
                    'account_id': account.id,
                    'account_type': account_type,
                    'old_rate': float(old_rate),
                    'new_rate': float(new_rate)
                }
            )
            
        db.session.commit() 