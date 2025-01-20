# 公司模块
from extensions import db

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    industry = db.Column(db.String(50), nullable=False)
    capital = db.Column(db.Float, default=0.0)
    stock_count = db.Column(db.Integer, default=0)
    shareholders = db.Column(db.JSON)
    partners = db.Column(db.JSON)

    def __repr__(self):
        return f'<Company {self.name}>'

    def add_shareholder(self, shareholder_id, shares):
        """添加股东"""
        if self.shareholders is None:
            self.shareholders = {}
        self.shareholders[shareholder_id] = shares

    def add_partner(self, company_id):
        """添加合作伙伴"""
        if self.partners is None:
            self.partners = set()
        self.partners.add(company_id)

    def issue_shares(self, amount):
        """发行新股"""
        if amount <= 0:
            raise ValueError("发行数量必须大于0")
        self.stock_count += amount
        self.capital += amount * self.get_share_price()

    def get_share_price(self):
        """计算每股价格"""
        return self.capital / self.stock_count

    def distribute_dividend(self, amount):
        """分红"""
        if amount > self.capital:
            raise ValueError("分红金额超过公司资金")
        self.capital -= amount
        total_shares = sum(self.shareholders.values())
        for shareholder, shares in self.shareholders.items():
            dividend = (shares / total_shares) * amount
            # 这里需要实现向股东发放分红 