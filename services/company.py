from models import db, Company
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