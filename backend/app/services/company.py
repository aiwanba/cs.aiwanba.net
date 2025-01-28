from datetime import datetime
from decimal import Decimal
from app import db
from app.models.company import Company
from app.models.trade import Shareholding
from app.models.message import Message

class CompanyService:
    @staticmethod
    def create_company(name, stock_code, industry, total_shares, initial_price, founder_id):
        """创建公司"""
        # 检查公司名称是否已存在
        if Company.query.filter_by(name=name).first():
            return False, "公司名称已存在"
        
        # 检查股票代码是否已存在
        if Company.query.filter_by(stock_code=stock_code).first():
            return False, "股票代码已存在"
        
        try:
            # 创建公司
            company = Company(
                name=name,
                stock_code=stock_code,
                industry=industry,
                total_shares=total_shares,
                initial_price=initial_price,
                founder_id=founder_id
            )
            db.session.add(company)
            
            # 创建创始人持股记录
            shareholding = Shareholding(
                company_id=company.id,
                user_id=founder_id,
                shares=total_shares,
                cost_price=initial_price
            )
            db.session.add(shareholding)
            
            # 创建公司创建公告
            message = Message(
                type=2,  # 公司公告
                title=f"新公司上市: {name}",
                content=f"新公司{name}({stock_code})已成功注册上市，"
                       f"总股本{total_shares}股，发行价{initial_price}元",
                related_id=company.id,
                priority=2  # 中等优先级
            )
            db.session.add(message)
            
            db.session.commit()
            return True, company
        except Exception as e:
            db.session.rollback()
            return False, str(e)
    
    @staticmethod
    def get_company_list(page=1, per_page=10, industry=None):
        """获取公司列表"""
        query = Company.query
        
        if industry:
            query = query.filter_by(industry=industry)
        
        companies = query.order_by(Company.id.desc())\
                        .paginate(page=page, per_page=per_page, error_out=False)
        
        return {
            'items': [company.to_dict() for company in companies.items],
            'total': companies.total,
            'pages': companies.pages,
            'current_page': companies.page
        }
    
    @staticmethod
    def get_company_detail(company_id):
        """获取公司详情"""
        company = Company.query.get(company_id)
        if not company:
            return False, "公司不存在"
        
        # 获取公司详细信息
        detail = company.to_dict()
        # 获取前10大股东
        top_shareholders = company.get_top_shareholders(10)
        detail['top_shareholders'] = [
            {
                'user_id': holding.user_id,
                'username': holding.shareholder.username,
                'shares': holding.shares,
                'percentage': (holding.shares / company.total_shares) * 100
            }
            for holding in top_shareholders
        ]
        
        return True, detail
    
    @staticmethod
    def update_company_status(company_id, status):
        """更新公司状态"""
        company = Company.query.get(company_id)
        if not company:
            return False, "公司不存在"
        
        try:
            company.status = status
            db.session.commit()
            
            # 创建状态变更公告
            status_desc = {1: "正常", 2: "停牌", 0: "破产"}
            message = Message(
                type=2,
                title=f"公司状态变更: {company.name}",
                content=f"公司{company.name}({company.stock_code})状态已变更为{status_desc[status]}",
                related_id=company.id,
                priority=1  # 高优先级
            )
            db.session.add(message)
            db.session.commit()
            
            return True, company
        except Exception as e:
            db.session.rollback()
            return False, str(e) 