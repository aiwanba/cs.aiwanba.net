from app import db, websocket_service
from app.models.bank import Bank, BankAccount, Loan, AccountType, LoanStatus
from app.models.user import User
from app.utils.exceptions import BankError
from flask_socketio import emit
from datetime import datetime, timedelta
import redis
import json
import random

class BankService:
    def __init__(self):
        self.redis_client = redis.from_url('redis://localhost:6379/0')
        self.min_credit_score = 600  # 最低信用分
        self.max_loan_ratio = 5  # 最大贷款额度倍数
        
    def create_account(self, user_id, bank_id, account_type):
        """开设银行账户"""
        try:
            # 检查是否已有同类型账户
            existing = BankAccount.query.filter_by(
                user_id=user_id,
                bank_id=bank_id,
                account_type=account_type
            ).first()
            
            if existing:
                raise BankError("Account already exists")
            
            account = BankAccount(
                user_id=user_id,
                bank_id=bank_id,
                account_type=account_type
            )
            
            db.session.add(account)
            db.session.commit()
            
            return account
            
        except Exception as e:
            db.session.rollback()
            raise BankError(str(e))
    
    def deposit(self, account_id, amount):
        """存款"""
        try:
            account = BankAccount.query.get(account_id)
            if not account:
                raise BankError("Account not found")
            
            if amount <= 0:
                raise BankError("Invalid deposit amount")
            
            account.balance += amount
            
            # 更新银行总存款
            bank = Bank.query.get(account.bank_id)
            bank.total_deposits += amount
            
            db.session.commit()
            
            # 发送通知
            websocket_service.send_private_notification(
                account.user_id,
                'deposit',
                {
                    'account_id': account_id,
                    'amount': amount,
                    'balance': account.balance
                }
            )
            
            return account
            
        except Exception as e:
            db.session.rollback()
            raise BankError(str(e))
    
    def withdraw(self, account_id, amount):
        """取款"""
        try:
            account = BankAccount.query.get(account_id)
            if not account:
                raise BankError("Account not found")
            
            if amount <= 0:
                raise BankError("Invalid withdrawal amount")
            
            if account.balance + account.credit_limit < amount:
                raise BankError("Insufficient funds")
            
            account.balance -= amount
            
            # 更新银行总存款
            bank = Bank.query.get(account.bank_id)
            bank.total_deposits -= amount
            
            db.session.commit()
            
            # 发送通知
            websocket_service.send_private_notification(
                account.user_id,
                'withdraw',
                {
                    'account_id': account_id,
                    'amount': amount,
                    'balance': account.balance
                }
            )
            
            return account
            
        except Exception as e:
            db.session.rollback()
            raise BankError(str(e))
    
    def apply_loan(self, user_id, bank_id, amount, term_months, purpose=None, collateral=None):
        """申请贷款"""
        try:
            # 检查用户信用
            credit_score = self._check_credit_score(user_id)
            if credit_score < self.min_credit_score:
                raise BankError("Credit score too low")
            
            # 检查贷款额度
            if not self._check_loan_limit(user_id, bank_id, amount):
                raise BankError("Exceeds maximum loan limit")
            
            loan = Loan(
                user_id=user_id,
                bank_id=bank_id,
                amount=amount,
                term_months=term_months,
                purpose=purpose,
                collateral=collateral
            )
            
            db.session.add(loan)
            db.session.commit()
            
            # 自动审核小额贷款
            if amount <= 10000:
                self._auto_approve_loan(loan.id)
            
            return loan
            
        except Exception as e:
            db.session.rollback()
            raise BankError(str(e))
    
    def approve_loan(self, loan_id):
        """审批贷款"""
        try:
            loan = Loan.query.get(loan_id)
            if not loan:
                raise BankError("Loan not found")
            
            if loan.status != LoanStatus.PENDING.value:
                raise BankError("Loan is not pending")
            
            loan.approve()
            
            # 放款到用户账户
            account = BankAccount.query.filter_by(
                user_id=loan.user_id,
                bank_id=loan.bank_id,
                account_type=AccountType.CHECKING.value
            ).first()
            
            if account:
                account.balance += loan.amount
            
            # 更新银行贷款总额
            bank = Bank.query.get(loan.bank_id)
            bank.total_loans += loan.amount
            
            db.session.commit()
            
            # 发送通知
            websocket_service.send_private_notification(
                loan.user_id,
                'loan_approved',
                {
                    'loan_id': loan_id,
                    'amount': loan.amount,
                    'monthly_payment': loan.monthly_payment
                }
            )
            
            return loan
            
        except Exception as e:
            db.session.rollback()
            raise BankError(str(e))
    
    def make_loan_payment(self, loan_id, amount):
        """还款"""
        try:
            loan = Loan.query.get(loan_id)
            if not loan:
                raise BankError("Loan not found")
            
            if loan.status not in [LoanStatus.APPROVED.value, LoanStatus.ACTIVE.value]:
                raise BankError("Loan is not active")
            
            # 从用户账户扣款
            account = BankAccount.query.filter_by(
                user_id=loan.user_id,
                bank_id=loan.bank_id,
                account_type=AccountType.CHECKING.value
            ).first()
            
            if not account or account.balance < amount:
                raise BankError("Insufficient funds")
            
            # 执行还款
            if loan.make_payment(amount):
                account.balance -= amount
                db.session.commit()
                
                # 发送通知
                websocket_service.send_private_notification(
                    loan.user_id,
                    'loan_payment',
                    {
                        'loan_id': loan_id,
                        'amount': amount,
                        'remaining': loan.remaining_amount
                    }
                )
                
                return loan
            else:
                raise BankError("Payment amount too small")
            
        except Exception as e:
            db.session.rollback()
            raise BankError(str(e))
    
    def _check_credit_score(self, user_id):
        """检查用户信用分"""
        # TODO: 实现真实的信用评分系统
        return random.randint(500, 800)
    
    def _check_loan_limit(self, user_id, bank_id, amount):
        """检查贷款额度"""
        # 获取用户在该银行的存款总额
        accounts = BankAccount.query.filter_by(
            user_id=user_id,
            bank_id=bank_id
        ).all()
        
        total_deposits = sum(account.balance for account in accounts)
        
        # 贷款额度不能超过存款的指定倍数
        return amount <= total_deposits * self.max_loan_ratio
    
    def _auto_approve_loan(self, loan_id):
        """自动审批小额贷款"""
        if random.random() < 0.8:  # 80%的通过率
            self.approve_loan(loan_id)
    
    def get_account_balance(self, user_id):
        """查询账户余额"""
        account = self._get_user_account(user_id)
        return {
            'balance': account.balance,
            'interest_earned': account.interest_earned
        }
    
    def get_user_loans(self, user_id):
        """获取用户贷款列表"""
        loans = Loan.query.filter_by(user_id=user_id).all()
        return [loan.to_dict() for loan in loans]
    
    def get_current_interest_rate(self):
        """获取当前利率"""
        # 从Redis缓存获取
        rate = self.redis_client.get('current_interest_rate')
        if rate:
            return json.loads(rate)
            
        # 如果没有缓存，计算新利率
        banks = Bank.query.all()
        avg_rate = sum(bank.interest_rate for bank in banks) / len(banks) if banks else 0.05
        
        data = {
            'base_rate': avg_rate,
            'loan_rate': avg_rate * 1.5,
            'updated_at': datetime.utcnow().isoformat()
        }
        
        # 缓存利率（1小时）
        self.redis_client.setex('current_interest_rate', 3600, json.dumps(data))
        return data
    
    def _get_user_account(self, user_id):
        """获取用户银行账户"""
        account = BankAccount.query.filter_by(user_id=user_id).first()
        if not account:
            raise BankError("Bank account not found", 404)
        return account 