# 交易所模块
from flask_sqlalchemy import SQLAlchemy
from extensions import db
from models.company import Company

class Exchange(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    listed = db.Column(db.Boolean, default=False)

    @staticmethod
    def list_company(company_id):
        exchange = Exchange(company_id=company_id, listed=True)
        db.session.add(exchange)
        db.session.commit()

    @staticmethod
    def delist_company(company_id):
        exchange = Exchange.query.filter_by(company_id=company_id).first()
        if exchange:
            db.session.delete(exchange)
            db.session.commit()

    def calculate_market_cap(self):
        """计算总市值"""
        total = 0
        for company_id, stock in self.stocks.items():
            total += stock.price * stock.total_shares
        return total

    def get_top_companies(self, n=5):
        """获取市值最高的公司"""
        companies = []
        for company_id, stock in self.stocks.items():
            market_cap = stock.price * stock.total_shares
            companies.append((company_id, market_cap))
        return sorted(companies, key=lambda x: x[1], reverse=True)[:n]

    def margin_trading(self, company_id, amount):
        """融资融券"""
        company = Company.query.get(company_id)
        if company:
            company.capital += amount
            db.session.commit() 