from app import db
from app.models.bank import Bank, BankAccount, Loan
from app.models.user import User
from app.utils.exceptions import BankError
from flask_socketio import emit
from datetime import datetime, timedelta
import redis
import json

class BankService:
    def __init__(self):
        self.redis_client = redis.from_url('redis://localhost:6379/0')
        
    def create_account(self, user_id, bank_id):
        """创建银行账户"""
        # 检查是否已有账户
        existing_account = BankAccount.query.filter_by(
            user_id=user_id,
            bank_id=bank_id
        ).first()
        
        if existing_account:
            raise BankError("Account already exists")
            
        bank = Bank.query.get(bank_id)
        if not bank:
            raise BankError("Bank not found", 404)
            
        try:
            account = BankAccount(
                bank_id=bank_id,
                user_id=user_id
            )
            db.session.add(account)
            db.session.commit()
            
            emit('account_created', account.to_dict(), room=str(user_id))
            return account
            
        except Exception as e:
            db.session.rollback()
            raise BankError(str(e))
    
    def deposit(self, user_id, amount):
        """存款"""
        if amount <= 0:
            raise BankError("Amount must be positive")
            
        account = self._get_user_account(user_id)
        user = User.query.get(user_id)
        
        if user.balance < amount:
            raise BankError("Insufficient balance in user wallet")
            
        try:
            # 从用户钱包转移到银行账户
            user.update_balance(-amount)
            account.deposit(amount)
            
            # 计算利息（简化版）
            interest_rate = account.bank.interest_rate
            interest = amount * interest_rate
            account.interest_earned += interest
            
            db.session.commit()
            
            emit('deposit_made', {
                'amount': amount,
                'new_balance': account.balance,
                'interest_earned': account.interest_earned
            }, room=str(user_id))
            
            return {
                'success': True,
                'new_balance': account.balance,
                'interest_earned': account.interest_earned
            }
            
        except Exception as e:
            db.session.rollback()
            raise BankError(str(e))
    
    def withdraw(self, user_id, amount):
        """取款"""
        if amount <= 0:
            raise BankError("Amount must be positive")
            
        account = self._get_user_account(user_id)
        
        if account.balance < amount:
            raise BankError("Insufficient funds in bank account")
            
        try:
            # 从银行账户转移到用户钱包
            success = account.withdraw(amount)
            if success:
                user = User.query.get(user_id)
                user.update_balance(amount)
                
                emit('withdrawal_made', {
                    'amount': amount,
                    'new_balance': account.balance
                }, room=str(user_id))
                
                return {
                    'success': True,
                    'new_balance': account.balance
                }
            else:
                raise BankError("Withdrawal failed")
                
        except Exception as e:
            db.session.rollback()
            raise BankError(str(e))
    
    def apply_loan(self, user_id, amount, term_months):
        """申请贷款"""
        if amount <= 0:
            raise BankError("Loan amount must be positive")
            
        if term_months < 1 or term_months > 360:  # 最长30年
            raise BankError("Invalid loan term")
            
        account = self._get_user_account(user_id)
        bank = account.bank
        
        # 简单的贷款审核逻辑
        if amount > account.balance * 10:  # 贷款额度不能超过存款的10倍
            raise BankError("Loan amount exceeds maximum allowed")
            
        try:
            loan = Loan(
                bank_id=bank.id,
                user_id=user_id,
                amount=amount,
                interest_rate=bank.interest_rate * 1.5,  # 贷款利率为存款利率的1.5倍
                term_months=term_months,
                remaining_amount=amount
            )
            
            db.session.add(loan)
            bank.total_loans += amount
            
            # 将贷款金额转入用户钱包
            user = User.query.get(user_id)
            user.update_balance(amount)
            
            db.session.commit()
            
            emit('loan_approved', loan.to_dict(), room=str(user_id))
            return loan
            
        except Exception as e:
            db.session.rollback()
            raise BankError(str(e))
    
    def repay_loan(self, loan_id, user_id, amount):
        """还款"""
        if amount <= 0:
            raise BankError("Amount must be positive")
            
        loan = Loan.query.get(loan_id)
        if not loan or loan.user_id != user_id:
            raise BankError("Loan not found", 404)
            
        if loan.status != 'active':
            raise BankError("Loan is not active")
            
        user = User.query.get(user_id)
        if user.balance < amount:
            raise BankError("Insufficient funds in wallet")
            
        try:
            success = loan.make_payment(amount)
            if success:
                user.update_balance(-amount)
                loan.bank.total_loans -= amount
                
                emit('loan_payment_made', {
                    'loan_id': loan_id,
                    'amount': amount,
                    'remaining': loan.remaining_amount
                }, room=str(user_id))
                
                return {
                    'success': True,
                    'remaining_amount': loan.remaining_amount,
                    'status': loan.status
                }
            else:
                raise BankError("Payment failed")
                
        except Exception as e:
            db.session.rollback()
            raise BankError(str(e))
    
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