from extensions import db

# 股票交易模块
class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    shareholder_id = db.Column(db.Integer)
    shares = db.Column(db.Integer)

    @staticmethod
    def buy_stock(company_id, shareholder_id, shares):
        stock = Stock(company_id=company_id, shareholder_id=shareholder_id, shares=shares)
        db.session.add(stock)
        db.session.commit()

    @staticmethod
    def sell_stock(stock_id):
        stock = Stock.query.get(stock_id)
        if stock:
            db.session.delete(stock)
            db.session.commit()

    def buy(self, buyer_id, shares):
        """购买股票"""
        if shares > self.shares:
            raise ValueError("购买数量超过持有数量")
        self.shareholder_id = buyer_id
        self.shares -= shares

    def sell(self, seller_id, shares):
        """出售股票"""
        if self.shares < shares:
            raise ValueError("出售数量超过持有数量")
        self.shareholder_id = seller_id
        self.shares -= shares

    def split_shares(self, ratio):
        """股票分割"""
        if ratio <= 1:
            raise ValueError("分割比例必须大于1")
        self.shares *= ratio

    def reverse_split(self, ratio):
        """股票合并"""
        if ratio <= 1:
            raise ValueError("合并比例必须大于1")
        self.shares //= ratio

    def calculate_dividend(self, amount):
        """计算每股分红"""
        return amount / self.shares 