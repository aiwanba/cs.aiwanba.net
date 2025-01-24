from app import db
from app.models.company import Company
from app.utils.exceptions import CompanyError
from sqlalchemy.exc import IntegrityError
from flask_socketio import emit

class CompanyService:
    def create_company(self, name, symbol, description, total_shares, owner_id):
        """创建新公司"""
        try:
            company = Company(
                name=name,
                symbol=symbol,
                description=description,
                total_shares=total_shares,
                owner_id=owner_id
            )
            db.session.add(company)
            db.session.commit()
            
            # 发送WebSocket通知
            emit('company_created', company.to_dict(), broadcast=True)
            return company
            
        except IntegrityError:
            db.session.rollback()
            raise CompanyError("Company name or symbol already exists")
    
    def get_companies(self, page=1, per_page=10):
        """获取公司列表（分页）"""
        return Company.query.paginate(
            page=page, 
            per_page=per_page,
            error_out=False
        )
    
    def get_company_by_id(self, company_id):
        """根据ID获取公司"""
        company = Company.query.get(company_id)
        if not company:
            raise CompanyError("Company not found", 404)
        return company
    
    def update_company(self, company_id, owner_id, **kwargs):
        """更新公司信息"""
        company = self.get_company_by_id(company_id)
        
        if company.owner_id != owner_id:
            raise CompanyError("Not authorized to update this company", 403)
        
        try:
            for key, value in kwargs.items():
                if hasattr(company, key):
                    setattr(company, key, value)
            
            db.session.commit()
            
            # 发送WebSocket通知
            emit('company_updated', company.to_dict(), broadcast=True)
            return company
            
        except IntegrityError:
            db.session.rollback()
            raise CompanyError("Update failed - duplicate name or symbol")
    
    def update_stock_price(self, company_id, owner_id, new_price):
        """更新股票价格"""
        company = self.get_company_by_id(company_id)
        
        if company.owner_id != owner_id:
            raise CompanyError("Not authorized to update stock price", 403)
        
        if new_price <= 0:
            raise CompanyError("Stock price must be positive")
        
        company.current_price = new_price
        company.update_market_cap()
        
        # 发送WebSocket通知
        emit('stock_price_updated', {
            'company_id': company_id,
            'new_price': new_price,
            'market_cap': company.market_cap
        }, broadcast=True)
        
        return company 