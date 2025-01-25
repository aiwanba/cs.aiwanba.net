from models import db, Company, Transaction
from decimal import Decimal

class CompanyService:
    """公司服务"""
    
    @staticmethod
    def create_company(name, description, total_shares, initial_price, owner_id):
        """创建新公司"""
        # 检查公司名是否已存在
        if Company.query.filter_by(name=name).first():
            return False, "公司名称已存在"
            
        # 创建新公司
        company = Company(
            name=name,
            description=description,
            total_shares=total_shares,
            available_shares=total_shares,  # 初始所有股份都可交易
            current_price=Decimal(str(initial_price)),
            owner_id=owner_id
        )
        
        try:
            db.session.add(company)
            db.session.commit()
            return True, company
        except Exception as e:
            db.session.rollback()
            return False, f"创建失败：{str(e)}"
    
    @staticmethod
    def get_company_info(company_id):
        """获取公司信息"""
        company = Company.query.get(company_id)
        if not company:
            return None
            
        return {
            'id': company.id,
            'name': company.name,
            'description': company.description,
            'total_shares': company.total_shares,
            'available_shares': company.available_shares,
            'current_price': float(company.current_price),
            'owner_id': company.owner_id,
            'created_at': company.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    @staticmethod
    def get_company_list():
        """获取所有公司列表"""
        companies = Company.query.all()
        return [{
            'id': company.id,
            'name': company.name,
            'current_price': float(company.current_price),
            'available_shares': company.available_shares
        } for company in companies]
    
    @staticmethod
    def get_company_transactions(company_id, limit=10):
        """获取公司最近交易历史"""
        transactions = Transaction.query.filter_by(company_id=company_id)\
            .order_by(Transaction.created_at.desc())\
            .limit(limit)\
            .all()
        
        return [{
            'id': tx.id,
            'type': '买入' if tx.buyer_id != tx.company.owner_id else '卖出',
            'shares': tx.shares,
            'price': float(tx.price),
            'total_amount': float(tx.total_amount),
            'created_at': tx.created_at.strftime('%Y-%m-%d %H:%M:%S')
        } for tx in transactions] 