from extensions import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    balance = db.Column(db.Float, default=100000000.0)  # 初始资金1亿

    def get_assets(self):
        """
        获取用户资产详情
        返回格式：
        {
            "cash": 现金余额,
            "stocks": [
                {
                    "stock_id": 股票ID,
                    "symbol": 股票代码,
                    "name": 股票名称,
                    "quantity": 持有数量,
                    "current_price": 当前价格,
                    "total_value": 当前市值
                },
                ...
            ],
            "total_assets": 总资产（现金+所有股票市值）
        }
        """
        assets = {
            "cash": self.balance,
            "stocks": [],
            "total_assets": self.balance
        }
        
        # 获取用户持有的所有股票
        holdings = Holding.query.filter_by(user_id=self.id).all()
        
        for holding in holdings:
            stock = Stock.query.get(holding.stock_id)
            if stock:
                stock_value = {
                    "stock_id": stock.id,
                    "symbol": stock.symbol,
                    "name": stock.name,
                    "quantity": holding.quantity,
                    "current_price": stock.current_price,
                    "total_value": holding.quantity * stock.current_price
                }
                assets["stocks"].append(stock_value)
                assets["total_assets"] += stock_value["total_value"]
        
        return assets

class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    symbol = db.Column(db.String(10), unique=True, nullable=False)
    price = db.Column(db.Float, nullable=False)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    stock_id = db.Column(db.Integer, db.ForeignKey('stock.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(10), nullable=False)  # buy/sell
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

    # 添加与Stock的关系字段
    stock = db.relationship('Stock', backref='transactions') 