# 交易所模块
class Exchange:
    def __init__(self):
        self.listed_companies = set()  # 上市公司集合
        self.stocks = {}  # 股票信息 {公司ID: Stock对象}

    def list_company(self, company_id, stock):
        """公司上市"""
        if company_id in self.listed_companies:
            raise ValueError("公司已上市")
        self.listed_companies.add(company_id)
        self.stocks[company_id] = stock

    def delist_company(self, company_id):
        """公司退市"""
        if company_id not in self.listed_companies:
            raise ValueError("公司未上市")
        self.listed_companies.remove(company_id)
        del self.stocks[company_id]

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