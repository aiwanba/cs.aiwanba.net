from models import Bank, BankAccount, BankTransaction, User
from extensions import db
from decimal import Decimal
from services.websocket import WebSocketService

class BankService:
    @staticmethod
    def create_bank(owner_id, name):
        """创建银行"""
        # 检查名称是否已存在
        if Bank.query.filter_by(name=name).first():
            raise ValueError("银行名称已存在")
            
        bank = Bank(
            owner_id=owner_id,
            name=name,
            total_assets=Decimal('100000000'),  # 初始资产1亿
            reserve_ratio=0.1  # 初始准备金率10%
        )
        
        db.session.add(bank)
        db.session.commit()
        return bank
        
    @staticmethod
    def open_account(bank_id, user_id):
        """开户"""
        # 检查是否已有账户
        if BankAccount.query.filter_by(bank_id=bank_id, user_id=user_id).first():
            raise ValueError("该银行已有账户")
            
        account = BankAccount(
            bank_id=bank_id,
            user_id=user_id,
            balance=Decimal('0'),
            account_type='savings',
            interest_rate=0.03  # 年利率3%
        )
        
        db.session.add(account)
        db.session.commit()
        return account
        
    @staticmethod
    def deposit(account_id, amount):
        """存款"""
        try:
            account = BankAccount.query.get_or_404(account_id)
            user = User.query.get(account.user_id)
            
            if user.balance < amount:
                raise ValueError("用户余额不足")
            
            # 更新用户余额
            user.balance -= amount
            # 更新账户余额
            account.balance += amount
            # 更新银行总资产
            bank = Bank.query.get(account.bank_id)
            bank.total_assets += amount
            
            # 记录交易
            transaction = BankTransaction(
                account_id=account_id,
                transaction_type='deposit',
                amount=amount
            )
            
            db.session.add(transaction)
            db.session.commit()
            
            # 广播存款信息
            WebSocketService.broadcast_bank_update(
                bank.id,
                'deposit',
                {
                    'account_id': account_id,
                    'amount': float(amount),
                    'total_assets': float(bank.total_assets)
                }
            )
            
            return transaction
            
        except Exception as e:
            db.session.rollback()
            raise e
        
    @staticmethod
    def withdraw(account_id, amount):
        """取款"""
        account = BankAccount.query.get_or_404(account_id)
        
        if account.balance < amount:
            raise ValueError("账户余额不足")
            
        bank = Bank.query.get(account.bank_id)
        available_cash = bank.total_assets * (1 - bank.reserve_ratio)
        if amount > available_cash:
            raise ValueError("银行可用现金不足")
            
        # 更新账户余额
        account.balance -= amount
        # 更新用户余额
        user = User.query.get(account.user_id)
        user.balance += amount
        # 更新银行总资产
        bank.total_assets -= amount
        
        # 记录交易
        transaction = BankTransaction(
            account_id=account_id,
            transaction_type='withdraw',
            amount=amount
        )
        
        db.session.add(transaction)
        db.session.commit()
        return transaction
        
    @staticmethod
    def apply_loan(account_id, amount, duration_months):
        """申请贷款"""
        account = BankAccount.query.get_or_404(account_id)
        bank = Bank.query.get(account.bank_id)
        
        # 检查银行可贷资金
        available_loan = bank.total_assets * (1 - bank.reserve_ratio)
        if amount > available_loan:
            raise ValueError("银行可贷资金不足")
            
        # 检查用户信用（这里简化处理，实际应该有更复杂的信用评估）
        user = User.query.get(account.user_id)
        if account.balance < amount * 0.1:  # 要求账户余额不低于贷款金额的10%
            raise ValueError("账户余额不足，无法获得贷款")
            
        # 创建贷款账户
        loan_account = BankAccount(
            bank_id=account.bank_id,
            user_id=account.user_id,
            balance=Decimal(str(amount)),
            account_type='loan',
            interest_rate=0.08,  # 贷款年利率8%
            loan_duration=duration_months
        )
        
        # 更新用户余额
        user.balance += amount
        # 更新银行总资产
        bank.total_assets -= amount
        
        # 记录交易
        transaction = BankTransaction(
            account_id=loan_account.id,
            transaction_type='loan',
            amount=amount
        )
        
        db.session.add(loan_account)
        db.session.add(transaction)
        db.session.commit()
        
        return loan_account, transaction
        
    @staticmethod
    def repay_loan(loan_account_id, amount):
        """还款"""
        loan_account = BankAccount.query.get_or_404(loan_account_id)
        if loan_account.account_type != 'loan':
            raise ValueError("不是贷款账户")
            
        if amount > loan_account.balance:
            raise ValueError("还款金额超过贷款余额")
            
        user = User.query.get(loan_account.user_id)
        if user.balance < amount:
            raise ValueError("用户余额不足")
            
        # 更新用户余额
        user.balance -= amount
        # 更新贷款余额
        loan_account.balance -= amount
        # 更新银行总资产
        bank = Bank.query.get(loan_account.bank_id)
        bank.total_assets += amount
        
        # 记录交易
        transaction = BankTransaction(
            account_id=loan_account_id,
            transaction_type='repay',
            amount=amount
        )
        
        db.session.add(transaction)
        
        # 如果贷款已还清，关闭贷款账户
        if loan_account.balance == 0:
            db.session.delete(loan_account)
            
        db.session.commit()
        return transaction 