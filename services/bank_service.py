from models import db
from models.bank import BankAccount, BankTransaction
from datetime import datetime

class BankService:
    """银行业务服务"""
    
    @staticmethod
    def create_account(company_id, initial_balance=0.0):
        """创建银行账户"""
        account = BankAccount(
            company_id=company_id,
            balance=initial_balance
        )
        db.session.add(account)
        db.session.commit()
        return account
    
    @staticmethod
    def get_account(account_id):
        """获取账户信息"""
        return BankAccount.query.get(account_id)
    
    @staticmethod
    def deposit(account_id, amount, description=None):
        """存款"""
        account = BankService.get_account(account_id)
        if account:
            account.deposit(amount)
            # 记录交易
            transaction = BankTransaction(
                account_id=account_id,
                transaction_type='deposit',
                amount=amount,
                description=description
            )
            db.session.add(transaction)
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def withdraw(account_id, amount, description=None):
        """取款"""
        account = BankService.get_account(account_id)
        if account and account.withdraw(amount):
            # 记录交易
            transaction = BankTransaction(
                account_id=account_id,
                transaction_type='withdraw',
                amount=amount,
                description=description
            )
            db.session.add(transaction)
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def transfer(from_account_id, to_account_id, amount, description=None):
        """转账"""
        from_account = BankService.get_account(from_account_id)
        to_account = BankService.get_account(to_account_id)
        
        if from_account and to_account and from_account.transfer(to_account, amount):
            # 记录交易
            transaction = BankTransaction(
                account_id=from_account_id,
                transaction_type='transfer',
                amount=amount,
                target_account_id=to_account_id,
                description=description
            )
            db.session.add(transaction)
            db.session.commit()
            return True
        return False 