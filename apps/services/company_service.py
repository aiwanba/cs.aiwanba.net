from apps.models.company import Company
from apps.models.stock import StockHolding
from apps.models.news import News
from app import db

class CompanyService:
    @staticmethod
    def create_company(user, name, description, total_shares, initial_price):
        """创建公司"""
        # 检查用户余额是否足够支付发行成本
        issue_cost = float(initial_price) * total_shares * 0.1  # 发行成本为总市值的10%
        if float(user.balance) < issue_cost:
            return False, "余额不足以支付发行成本"
        
        # 创建公司
        company = Company(
            name=name,
            description=description,
            total_shares=total_shares,
            available_shares=total_shares,
            current_price=initial_price,
            owner_id=user.id
        )
        
        # 扣除发行成本
        user.balance -= issue_cost
        
        # 创建新闻
        news = News(
            title=f"新公司上市：{name}",
            content=f"{name}在股市成功上市，发行价格为{initial_price}，总股本{total_shares}股。",
            type='company',
            company_id=company.id,
            impact=0.01  # 小幅利好
        )
        
        db.session.add(company)
        db.session.add(news)
        db.session.commit()
        
        return True, company

    @staticmethod
    def update_company(company_id, **kwargs):
        """更新公司信息"""
        company = Company.query.get(company_id)
        if not company:
            return False, "公司不存在"
        
        # 更新允许修改的字段
        allowed_fields = ['description']
        for field, value in kwargs.items():
            if field in allowed_fields:
                setattr(company, field, value)
        
        db.session.commit()
        return True, company

    @staticmethod
    def get_market_overview():
        """获取市场概览"""
        companies = Company.query.all()
        market_data = []
        total_market_value = 0
        
        for company in companies:
            market_value = company.market_value()
            total_market_value += market_value
            market_data.append({
                'id': company.id,
                'name': company.name,
                'current_price': float(company.current_price),
                'total_shares': company.total_shares,
                'available_shares': company.available_shares,
                'market_value': market_value
            })
        
        return {
            'companies': market_data,
            'total_market_value': total_market_value,
            'company_count': len(companies)
        } 