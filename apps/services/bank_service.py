from datetime import datetime, timedelta
from apps.models.bank import BankAccount
from app import db

class BankService:
    # 基准利率配置
    RATES = {
        'savings': 0.03,  # 年化存款利率3%
        'loan': 0.06      # 年化贷款利率6%
    }
    
    @staticmethod
    def create_savings_account(user):
        """创建储蓄账户"""
        account = BankAccount(
            user_id=user.id,
            account_type='savings',
            balance=0,
            interest_rate=BankService.RATES['savings']
        )
        db.session.add(account)
        db.session.commit()
        return account
    
    @staticmethod
    def create_loan(user, amount, duration_days):
        """创建贷款"""
        # 检查用户信用和现有贷款
        existing_loan = BankAccount.query.filter_by(
            user_id=user.id,
            account_type='loan',
            status='active'
        ).first()
        
        if existing_loan:
            return False, "已有未还清的贷款"
            
        # 创建贷款账户
        loan = BankAccount(
            user_id=user.id,
            account_type='loan',
            balance=amount,
            interest_rate=BankService.RATES['loan'],
            end_date=datetime.utcnow() + timedelta(days=duration_days)
        )
        
        # 发放贷款到用户余额
        user.balance += amount
        
        db.session.add(loan)
        db.session.commit()
        return True, loan
    
    @staticmethod
    def deposit(account_id, amount):
        """存款"""
        account = BankAccount.query.get(account_id)
        if not account or account.account_type != 'savings':
            return False, "账户不存在或类型错误"
            
        if float(account.user.balance) < amount:
            return False, "余额不足"
            
        account.balance += amount
        account.user.balance -= amount
        
        db.session.commit()
        return True, "存款成功"
    
    @staticmethod
    def withdraw(account_id, amount):
        """取款"""
        account = BankAccount.query.get(account_id)
        if not account or account.account_type != 'savings':
            return False, "账户不存在或类型错误"
            
        if float(account.balance) < amount:
            return False, "存款余额不足"
            
        account.balance -= amount
        account.user.balance += amount
        
        db.session.commit()
        return True, "取款成功"
    
    @staticmethod
    def repay_loan(loan_id, amount):
        """还贷"""
        loan = BankAccount.query.get(loan_id)
        if not loan or loan.account_type != 'loan' or loan.status != 'active':
            return False, "贷款账户不存在或已结清"
            
        if float(loan.user.balance) < amount:
            return False, "余额不足"
            
        loan.balance -= amount
        loan.user.balance -= amount
        
        if float(loan.balance) <= 0:
            loan.status = 'closed'
            
        db.session.commit()
        return True, "还款成功"
    
    @staticmethod
    def calculate_daily_interest():
        """计算每日利息"""
        accounts = BankAccount.query.filter_by(status='active').all()
        for account in accounts:
            interest = account.calculate_interest()
            if account.account_type == 'savings':
                account.balance += interest
            else:  # loan
                account.balance += interest
                if datetime.utcnow() > account.end_date:
                    # 贷款逾期，上调利率
                    account.interest_rate = BankService.RATES['loan'] * 1.5
        db.session.commit() 