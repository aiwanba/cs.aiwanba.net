from models import db, BankAccount, BankLoan, BankTransaction, User, AIPlayer
from decimal import Decimal
from datetime import datetime, timedelta

class BankService:
    """银行服务"""
    
    @staticmethod
    def get_account(account_holder_id, account_type='player'):
        """获取银行账户"""
        if account_type == 'player':
            return BankAccount.query.filter_by(user_id=account_holder_id).first()
        else:
            return BankAccount.query.filter_by(ai_player_id=account_holder_id).first()
    
    @staticmethod
    def get_user_loans(user_id):
        """获取用户贷款列表"""
        return BankLoan.query.filter_by(user_id=user_id).all()
    
    @staticmethod
    def get_recent_transactions(account_id, limit=10):
        """获取最近交易记录"""
        return BankTransaction.query.filter_by(account_id=account_id)\
            .order_by(BankTransaction.created_at.desc())\
            .limit(limit).all()
    
    @staticmethod
    def create_account(account_holder_id, account_type='player', initial_balance=100000.00):
        """创建银行账户"""
        # 检查账户是否已存在
        existing_account = BankService.get_account(account_holder_id, account_type)
        if existing_account:
            return False, "已有银行账户"
            
        # 创建新账户
        account = BankAccount(
            account_type=account_type,
            balance=initial_balance
        )
        
        if account_type == 'player':
            account.user_id = account_holder_id
        else:
            account.ai_player_id = account_holder_id
            
        try:
            db.session.add(account)
            db.session.commit()
            return True, account
        except Exception as e:
            db.session.rollback()
            return False, str(e)
    
    @staticmethod
    def transfer(from_account_id, to_account_id, amount, description='转账'):
        """账户间转账"""
        from_account = BankAccount.query.get(from_account_id)
        to_account = BankAccount.query.get(to_account_id)
        
        if not all([from_account, to_account]):
            return False, "账户不存在"
            
        if from_account.balance < Decimal(str(amount)):
            return False, "余额不足"
            
        try:
            # 扣除转出账户金额
            from_account.balance -= Decimal(str(amount))
            # 记录转出交易
            from_transaction = BankTransaction(
                account_id=from_account_id,
                type='transfer_out',
                amount=amount,
                balance_after=from_account.balance,
                description=f"{description} - 转出"
            )
            
            # 增加转入账户金额
            to_account.balance += Decimal(str(amount))
            # 记录转入交易
            to_transaction = BankTransaction(
                account_id=to_account_id,
                type='transfer_in',
                amount=amount,
                balance_after=to_account.balance,
                description=f"{description} - 转入"
            )
            
            db.session.add(from_transaction)
            db.session.add(to_transaction)
            db.session.commit()
            
            return True, {"from": from_transaction, "to": to_transaction}
        except Exception as e:
            db.session.rollback()
            return False, str(e)
    
    @staticmethod
    def deposit(account_id, amount):
        """存款"""
        account = BankAccount.query.get(account_id)
        if not account:
            return False, "账户不存在"
            
        try:
            # 更新账户余额
            account.balance += Decimal(str(amount))
            
            # 记录交易
            transaction = BankTransaction(
                account_id=account_id,
                type='deposit',
                amount=amount,
                balance_after=account.balance,
                description='存款'
            )
            db.session.add(transaction)
            
            db.session.commit()
            return True, transaction
        except Exception as e:
            db.session.rollback()
            return False, str(e)
    
    @staticmethod
    def withdraw(account_id, amount):
        """取款"""
        account = BankAccount.query.get(account_id)
        if not account:
            return False, "账户不存在"
            
        if account.balance < Decimal(str(amount)):
            return False, "余额不足"
            
        try:
            # 更新账户余额
            account.balance -= Decimal(str(amount))
            
            # 记录交易
            transaction = BankTransaction(
                account_id=account_id,
                type='withdraw',
                amount=amount,
                balance_after=account.balance,
                description='取款'
            )
            db.session.add(transaction)
            
            db.session.commit()
            return True, transaction
        except Exception as e:
            db.session.rollback()
            return False, str(e)
    
    @staticmethod
    def apply_loan(user_id, amount, term_months):
        """申请贷款"""
        # 检查用户信用
        user = User.query.get(user_id)
        if not user:
            return False, "用户不存在"
            
        # 根据用户资产确定利率
        total_assets = float(user.balance)  # 后续可以加入股票市值
        if total_assets > 1000000:
            interest_rate = 4.5  # 优质客户
        elif total_assets > 500000:
            interest_rate = 5.0  # 良好客户
        else:
            interest_rate = 5.5  # 普通客户
            
        # 创建贷款
        loan = BankLoan(
            user_id=user_id,
            amount=amount,
            interest_rate=interest_rate,
            term_months=term_months,
            remaining_amount=amount
        )
        
        try:
            # 添加贷款记录
            db.session.add(loan)
            
            # 将贷款金额存入用户账户
            account = BankAccount.query.filter_by(user_id=user_id).first()
            if account:
                account.balance += Decimal(str(amount))
                
                # 记录交易
                transaction = BankTransaction(
                    account_id=account.id,
                    type='loan',
                    amount=amount,
                    balance_after=account.balance,
                    description=f'贷款发放（{term_months}个月，年利率{interest_rate}%）'
                )
                db.session.add(transaction)
            
            db.session.commit()
            return True, loan
        except Exception as e:
            db.session.rollback()
            return False, str(e)
    
    @staticmethod
    def repay_loan(loan_id, amount):
        """还款"""
        loan = BankLoan.query.get(loan_id)
        if not loan:
            return False, "贷款不存在"
            
        if loan.status != 'active':
            return False, "贷款已结清或逾期"
            
        if Decimal(str(amount)) > loan.remaining_amount:
            return False, "还款金额超过剩余待还金额"
            
        try:
            # 更新贷款剩余金额
            loan.remaining_amount -= Decimal(str(amount))
            if loan.remaining_amount == 0:
                loan.status = 'paid'
            
            # 从用户账户扣款
            account = BankAccount.query.filter_by(user_id=loan.user_id).first()
            if account:
                if account.balance < Decimal(str(amount)):
                    return False, "账户余额不足"
                    
                account.balance -= Decimal(str(amount))
                
                # 记录交易
                transaction = BankTransaction(
                    account_id=account.id,
                    type='repayment',
                    amount=amount,
                    balance_after=account.balance,
                    description='贷款还款'
                )
                db.session.add(transaction)
            
            db.session.commit()
            return True, loan
        except Exception as e:
            db.session.rollback()
            return False, str(e)
    
    @staticmethod
    def calculate_interest():
        """计算利息（每日运行）"""
        accounts = BankAccount.query.all()
        for account in accounts:
            # 计算日利息（年利率/365）
            daily_interest = float(account.balance) * float(account.interest_rate) / 100 / 365
            if daily_interest > 0:
                try:
                    # 更新账户余额
                    account.balance += Decimal(str(daily_interest))
                    
                    # 记录利息交易
                    transaction = BankTransaction(
                        account_id=account.id,
                        type='interest',
                        amount=daily_interest,
                        balance_after=account.balance,
                        description='利息收入'
                    )
                    db.session.add(transaction)
                    
                except Exception as e:
                    db.session.rollback()
                    print(f"计算利息失败: {str(e)}")
                    continue
                    
        db.session.commit() 