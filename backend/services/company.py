from models import Company, Stock
from extensions import db
from decimal import Decimal

class CompanyService:
    @staticmethod
    def create_company(owner_id, name, industry, total_shares, initial_price):
        """创建新公司"""
        # 验证参数
        if total_shares < 100000 or total_shares > 1000000:
            raise ValueError("总股本必须在10万到100万股之间")
        if not (10 <= float(initial_price) <= 100):
            raise ValueError("初始股价必须在10-100元之间")
            
        # 创建公司
        company = Company(
            owner_id=owner_id,
            name=name,
            industry=industry,
            total_shares=total_shares,
            current_price=initial_price,
            cash_balance=Decimal('10000000')  # 初始资金1000万
        )
        
        db.session.add(company)
        db.session.flush()  # 获取company.id
        
        # 创建创始人初始股票
        initial_shares = int(Decimal('10000000') / Decimal(str(initial_price)))
        if initial_shares < total_shares * 0.2:  # 确保创始人持股不低于20%
            initial_shares = int(total_shares * 0.2)
            
        stock = Stock(
            company_id=company.id,
            holder_id=owner_id,
            amount=initial_shares
        )
        
        db.session.add(stock)
        db.session.commit()
        
        return company

    @staticmethod
    def get_company_info(company_id):
        """获取公司信息"""
        company = Company.query.get_or_404(company_id)
        stocks = Stock.query.filter_by(company_id=company_id).all()
        
        # 计算股东信息
        shareholders = []
        for stock in stocks:
            shareholders.append({
                'holder_id': stock.holder_id,
                'amount': stock.amount,
                'percentage': (stock.amount / company.total_shares) * 100
            })
            
        return {
            'id': company.id,
            'name': company.name,
            'industry': company.industry,
            'total_shares': company.total_shares,
            'current_price': float(company.current_price),
            'cash_balance': float(company.cash_balance),
            'shareholders': shareholders
        } 