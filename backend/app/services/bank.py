from datetime import datetime, timedelta
from decimal import Decimal
from app import db
from app.models.bank import Bank, Deposit, Loan
from app.models.message import Message
from app.services.transaction import TransactionService
from app.models.transaction import Transaction

class BankService:
    @staticmethod
    def create_bank(name, owner_id, capital, deposit_rate, loan_rate, reserve_ratio=10.00):
        """创建银行"""
        # 检查银行名称是否已存在
        if Bank.query.filter_by(name=name).first():
            return False, "银行名称已存在"
        
        try:
            # 创建银行
            bank = Bank(
                name=name,
                owner_id=owner_id,
                capital=capital,
                deposit_rate=deposit_rate,
                loan_rate=loan_rate,
                reserve_ratio=reserve_ratio
            )
            db.session.add(bank)
            db.session.flush()  # 获取bank.id
            
            # 创建资金流水
            success, result = TransactionService.create_transaction(
                user_id=owner_id,
                type=Transaction.TYPE_CREATE_BANK,
                amount=-capital,  # 负数表示支出
                related_id=bank.id,
                description=f"创建银行：{name}"
            )
            if not success:
                db.session.rollback()
                return False, result
            
            # 创建银行开业公告
            message = Message(
                type=1,  # 系统公告
                title=f"新银行开业: {name}",
                content=f"新银行{name}已开业，注册资本{capital}元，"
                       f"存款利率{deposit_rate}%，贷款利率{loan_rate}%，"
                       f"准备金率{reserve_ratio}%",
                priority=2  # 中等优先级
            )
            db.session.add(message)
            
            db.session.commit()
            return True, bank
        except Exception as e:
            db.session.rollback()
            return False, str(e)
    
    @staticmethod
    def create_deposit(bank_id, user_id, amount, term):
        """创建存款"""
        bank = Bank.query.get(bank_id)
        if not bank:
            return False, "银行不存在"
        
        if bank.status != 1:
            return False, "银行状态异常"
        
        try:
            # 将 amount 转换为 Decimal
            amount = Decimal(str(amount))
            
            start_date = datetime.utcnow()
            end_date = start_date + timedelta(days=term)
            
            deposit = Deposit(
                bank_id=bank_id,
                user_id=user_id,
                amount=amount,  # 已经是 Decimal 类型
                interest_rate=bank.deposit_rate,
                term=term,
                start_date=start_date,
                end_date=end_date
            )
            db.session.add(deposit)
            
            # 更新银行存款总额 (现在两者都是 Decimal 类型)
            bank.total_deposit += amount
            
            db.session.commit()
            return True, deposit
        except Exception as e:
            db.session.rollback()
            return False, str(e)
    
    @staticmethod
    def create_loan(bank_id, user_id, amount, term, collateral_type, collateral_id):
        """创建贷款"""
        bank = Bank.query.get(bank_id)
        if not bank:
            return False, "银行不存在"
        
        if bank.status != 1:
            return False, "银行状态异常"
        
        if not bank.can_loan(amount):
            return False, "银行可贷资金不足"
        
        try:
            # 创建贷款记录
            loan = Loan(
                bank_id=bank_id,
                user_id=user_id,
                amount=amount,
                interest_rate=bank.loan_rate,
                term=term,
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() + timedelta(days=term),
                collateral_type=collateral_type,
                collateral_id=collateral_id
            )
            db.session.add(loan)
            
            # 更新银行贷款总额
            bank.total_loan += amount
            
            db.session.commit()
            return True, loan
        except Exception as e:
            db.session.rollback()
            return False, str(e)
    
    @staticmethod
    def get_bank_list(page=1, per_page=10):
        """获取银行列表"""
        banks = Bank.query.order_by(Bank.id.desc())\
                         .paginate(page=page, per_page=per_page, error_out=False)
        
        return {
            'items': [bank.to_dict() for bank in banks.items],
            'total': banks.total,
            'pages': banks.pages,
            'current_page': banks.page
        }
    
    @staticmethod
    def get_bank_detail(bank_id):
        """获取银行详情"""
        bank = Bank.query.get(bank_id)
        if not bank:
            return False, "银行不存在"
        
        detail = bank.to_dict()
        # 添加其他统计信息
        detail['deposit_count'] = len(bank.deposits)
        detail['loan_count'] = len(bank.loans)
        detail['available_funds'] = bank.get_available_funds()
        
        return True, detail
    
    @staticmethod
    def update_rates(bank_id, deposit_rate=None, loan_rate=None):
        """更新利率"""
        bank = Bank.query.get(bank_id)
        if not bank:
            return False, "银行不存在"
        
        try:
            if deposit_rate is not None:
                bank.deposit_rate = deposit_rate
            if loan_rate is not None:
                bank.loan_rate = loan_rate
            
            # 创建利率变更公告
            message = Message(
                type=2,
                title=f"银行利率变更: {bank.name}",
                content=f"银行{bank.name}利率已更新，"
                       f"存款利率{bank.deposit_rate}%，贷款利率{bank.loan_rate}%",
                priority=2
            )
            db.session.add(message)
            
            db.session.commit()
            return True, bank
        except Exception as e:
            db.session.rollback()
            return False, str(e) 