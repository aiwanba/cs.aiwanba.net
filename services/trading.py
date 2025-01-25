from decimal import Decimal
from models import db, Company, StockHolding, Transaction, User
from services.bank import BankService

class TradingService:
    """交易服务"""
    
    @staticmethod
    def buy_stock(buyer_id, company_id, shares, price):
        """买入股票"""
        # 获取买家银行账户
        buyer_account = BankService.get_account(buyer_id, 'player')
        if not buyer_account:
            return False, "买家银行账户不存在"
            
        # 获取公司所有者银行账户
        company = Company.query.get(company_id)
        if not company:
            return False, "公司不存在"
            
        seller_account = BankService.get_account(company.owner_id, 'player')
        if not seller_account:
            return False, "卖家银行账户不存在"
            
        # 计算交易总额
        total_amount = Decimal(str(price)) * shares
        
        # 执行转账
        success, result = BankService.transfer(
            buyer_account.id,
            seller_account.id,
            total_amount,
            f"股票交易 - 公司ID:{company_id}"
        )
        
        if not success:
            return False, result
            
        try:
            # 检查可用股份
            if company.available_shares < shares:
                return False, "可用股份不足"
            
            # 更新公司股份
            company.available_shares -= shares
            
            # 更新买家持股
            stock_holding = StockHolding.query.filter_by(
                user_id=buyer_id,
                company_id=company_id
            ).first()
            
            if stock_holding:
                stock_holding.shares += shares
            else:
                stock_holding = StockHolding(
                    user_id=buyer_id,
                    company_id=company_id,
                    shares=shares
                )
                db.session.add(stock_holding)
            
            # 更新公司当前股价
            company.current_price = price
            
            db.session.commit()
            return True, "交易成功"
            
        except Exception as e:
            db.session.rollback()
            return False, f"交易失败：{str(e)}"
    
    @staticmethod
    def sell_stock(seller_id, company_id, shares, price):
        """卖出股票"""
        # 获取卖家银行账户
        seller_account = BankService.get_account(seller_id, 'player')
        if not seller_account:
            return False, "卖家银行账户不存在"
        
        # 检查持股数量
        stock_holding = StockHolding.query.filter_by(
            user_id=seller_id,
            company_id=company_id
        ).first()
        
        if not stock_holding or stock_holding.shares < shares:
            return False, "持股不足"
        
        # 获取公司和公司所有者账户
        company = Company.query.get(company_id)
        if not company:
            return False, "公司不存在"
        
        buyer_account = BankService.get_account(company.owner_id, 'player')
        if not buyer_account:
            return False, "买家银行账户不存在"
        
        # 计算交易总额
        total_amount = Decimal(str(price)) * shares
        
        try:
            # 更新卖家持股
            stock_holding.shares -= shares
            if stock_holding.shares == 0:
                db.session.delete(stock_holding)
            
            # 更新公司可用股份
            company.available_shares += shares
            
            # 执行转账
            success, result = BankService.transfer(
                buyer_account.id,
                seller_account.id,
                total_amount,
                f"股票交易 - 公司ID:{company_id}"
            )
            
            if not success:
                db.session.rollback()
                return False, result
            
            # 更新公司当前股价
            company.current_price = price
            
            db.session.commit()
            return True, "交易成功"
            
        except Exception as e:
            db.session.rollback()
            return False, f"交易失败：{str(e)}"
    
    @staticmethod
    def get_stock_holdings(user_id):
        """获取用户持股信息"""
        holdings = StockHolding.query.filter_by(user_id=user_id).all()
        result = []
        for holding in holdings:
            company = Company.query.get(holding.company_id)
            result.append({
                'company_id': company.id,
                'company_name': company.name,
                'shares': holding.shares,
                'current_price': float(company.current_price),
                'total_value': float(company.current_price * holding.shares)
            })
        return result 