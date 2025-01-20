# 银行模块
from flask_sqlalchemy import SQLAlchemy
from extensions import db
from models.company import Company

class Bank(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    capital = db.Column(db.Float)

    def __init__(self, name, capital):
        self.name = name
        self.capital = capital

    def loan(self, company_id, amount):
        """贷款"""
        company = Company.query.get(company_id)
        if company and self.capital >= amount:
            company.capital += amount
            self.capital -= amount
            db.session.commit()

    def grant_loan(self, company_id, amount):
        """发放贷款"""
        if amount > self.capital:
            raise ValueError("贷款金额超过银行资金")
        self.capital -= amount

    def repay_loan(self, company_id, amount):
        """偿还贷款"""
        if self.capital < amount:
            raise ValueError("还款金额超过银行资金")
        self.capital += amount

    def calculate_interest(self, company_id, rate, period):
        """计算贷款利息"""
        # 这里需要实现计算贷款利息的逻辑
        raise NotImplementedError("计算贷款利息的方法需要实现")

    def check_credit(self, company_id):
        """评估公司信用"""
        # 这里可以添加更复杂的信用评估逻辑
        loan_amount = self.capital
        if loan_amount > 1000000:
            return "C"
        elif loan_amount > 500000:
            return "B"
        else:
            return "A"

    def deposit(self, company_id, amount):
        """存款"""
        company = Company.query.get(company_id)
        if company and company.capital >= amount:
            company.capital -= amount
            self.capital += amount
            db.session.commit() 