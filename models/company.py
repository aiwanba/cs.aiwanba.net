# 公司模块
class Company:
    def __init__(self, name, industry, capital, stock_count):
        self.name = name  # 公司名称
        self.industry = industry  # 所属行业
        self.capital = capital  # 公司资金
        self.stock_count = stock_count  # 股票数量
        self.shareholders = {}  # 股东信息 {股东ID: 持股数量}
        self.partners = set()  # 合作伙伴公司ID集合

    def add_shareholder(self, shareholder_id, shares):
        """添加股东"""
        self.shareholders[shareholder_id] = shares

    def add_partner(self, company_id):
        """添加合作伙伴"""
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