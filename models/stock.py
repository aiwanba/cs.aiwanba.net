# 股票交易模块
class Stock:
    def __init__(self, company_id, total_shares, price):
        self.company_id = company_id  # 所属公司ID
        self.total_shares = total_shares  # 总股数
        self.price = price  # 当前股价
        self.holders = {}  # 股东持股信息 {股东ID: 持股数量}

    def buy(self, buyer_id, shares):
        """购买股票"""
        if shares > self.total_shares:
            raise ValueError("购买数量超过总股数")
        self.holders[buyer_id] = self.holders.get(buyer_id, 0) + shares
        self.total_shares -= shares

    def sell(self, seller_id, shares):
        """出售股票"""
        if self.holders.get(seller_id, 0) < shares:
            raise ValueError("出售数量超过持有数量")
        self.holders[seller_id] -= shares
        self.total_shares += shares

    def split_shares(self, ratio):
        """股票分割"""
        if ratio <= 1:
            raise ValueError("分割比例必须大于1")
        self.total_shares *= ratio
        for holder in self.holders:
            self.holders[holder] *= ratio

    def reverse_split(self, ratio):
        """股票合并"""
        if ratio <= 1:
            raise ValueError("合并比例必须大于1")
        self.total_shares //= ratio
        for holder in self.holders:
            self.holders[holder] //= ratio

    def calculate_dividend(self, amount):
        """计算每股分红"""
        return amount / self.total_shares 