from app import db
from models.bank import BankAccount, BankTransaction
from models.company import Company
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
    def create_transaction(account_id, transaction_type, amount, target_account_id=None, description=None):
        """记录交易"""
        transaction = BankTransaction(
            account_id=account_id,
            transaction_type=transaction_type,
            amount=amount,
            target_account_id=target_account_id,
            description=description
        )
        db.session.add(transaction)
        db.session.commit()
        return transaction
    
    @staticmethod
    def deposit(account_id, amount, description=None):
        """存款服务"""
        account = BankAccount.query.get(account_id)
        if account:
            account.deposit(amount)
            BankService.create_transaction(
                account_id=account_id,
                transaction_type='deposit',
                amount=amount,
                description=description
            )
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def withdraw(account_id, amount, description=None):
        """取款服务"""
        account = BankAccount.query.get(account_id)
        if account and account.withdraw(amount):
            BankService.create_transaction(
                account_id=account_id,
                transaction_type='withdraw',
                amount=amount,
                description=description
            )
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def transfer(from_account_id, to_account_id, amount, description=None):
        """转账服务"""
        from_account = BankAccount.query.get(from_account_id)
        to_account = BankAccount.query.get(to_account_id)
        
        if from_account and to_account:
            if from_account.transfer(to_account, amount):
                # 记录转出交易
                BankService.create_transaction(
                    account_id=from_account_id,
                    transaction_type='transfer_out',
                    amount=amount,
                    target_account_id=to_account_id,
                    description=description
                )
                # 记录转入交易
                BankService.create_transaction(
                    account_id=to_account_id,
                    transaction_type='transfer_in',
                    amount=amount,
                    target_account_id=from_account_id,
                    description=description
                )
                db.session.commit()
                return True
        return False 