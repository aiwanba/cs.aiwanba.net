import locust
from locust import HttpUser, task, between

class StockGameUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(3)
    def view_market(self):
        """查看市场数据"""
        self.client.get('/api/market/data')
    
    @task(2)
    def view_news(self):
        """查看新闻"""
        self.client.get('/api/news/list')
    
    @task(1)
    def trade_stock(self):
        """交易股票"""
        self.client.post('/api/trading/buy', json={
            'company_id': 1,
            'shares': 100,
            'price': 10.0
        }) 