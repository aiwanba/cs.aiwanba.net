from . import db, BaseModel
from decimal import Decimal
from datetime import datetime

class Shareholding(BaseModel):
    """股权模型"""
    __tablename__ = 'shareholdings'
    
    company_id = db.Column(db.BigInteger, db.ForeignKey('companies.id'), nullable=False)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    shares = db.Column(db.BigInteger, nullable=False)  # 持股数量
    cost_price = db.Column(db.DECIMAL(10, 2), nullable=False)  # 成本价
    pledged_shares = db.Column(db.BigInteger, default=0)  # 质押股份数
    
    __table_args__ = (
        db.UniqueConstraint('company_id', 'user_id', name='unique_holding'),
    )
    
    def update_shares(self, quantity, price):
        """更新持股数量和成本价"""
        if quantity > 0:  # 买入
            new_total = self.shares + quantity
            new_cost = ((self.shares * self.cost_price) + (quantity * price)) / new_total
            self.shares = new_total
            self.cost_price = new_cost
        else:  # 卖出
            self.shares += quantity  # quantity是负数
        db.session.commit()
    
    def can_sell(self, quantity):
        """检查是否可以卖出"""
        return self.shares - self.pledged_shares >= quantity
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'company_id': self.company_id,
            'user_id': self.user_id,
            'shares': self.shares,
            'cost_price': float(self.cost_price),
            'pledged_shares': self.pledged_shares,
            'market_value': float(self.shares * self.company.current_price),
            'profit_rate': float((self.company.current_price - self.cost_price) / self.cost_price * 100),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Order(BaseModel):
    """交易订单模型"""
    __tablename__ = 'orders'
    
    company_id = db.Column(db.BigInteger, db.ForeignKey('companies.id'), nullable=False)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    order_type = db.Column(db.Integer, nullable=False)  # 1-买入，2-卖出
    price_type = db.Column(db.Integer, nullable=False)  # 1-市价，2-限价
    price = db.Column(db.DECIMAL(10, 2))  # 委托价格
    quantity = db.Column(db.BigInteger, nullable=False)  # 委托数量
    filled_quantity = db.Column(db.BigInteger, default=0)  # 已成交数量
    status = db.Column(db.Integer, default=1)  # 1-未成交，2-部分成交，3-全部成交，4-已撤销
    
    # 关联关系
    buy_trades = db.relationship('Trade', foreign_keys='Trade.buy_order_id', backref='buy_order', lazy=True)
    sell_trades = db.relationship('Trade', foreign_keys='Trade.sell_order_id', backref='sell_order', lazy=True)
    
    def can_cancel(self):
        """检查是否可以撤单"""
        return self.status in [1, 2]  # 未成交或部分成交可以撤单
    
    def cancel(self):
        """撤销订单"""
        if not self.can_cancel():
            return False
        self.status = 4
        db.session.commit()
        return True
    
    def update_filled(self, filled_quantity):
        """更新成交数量"""
        self.filled_quantity += filled_quantity
        if self.filled_quantity >= self.quantity:
            self.status = 3  # 全部成交
        elif self.filled_quantity > 0:
            self.status = 2  # 部分成交
        db.session.commit()
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'company_id': self.company_id,
            'user_id': self.user_id,
            'order_type': self.order_type,
            'price_type': self.price_type,
            'price': float(self.price) if self.price else None,
            'quantity': self.quantity,
            'filled_quantity': self.filled_quantity,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Trade(BaseModel):
    """成交记录模型"""
    __tablename__ = 'trades'
    
    company_id = db.Column(db.BigInteger, db.ForeignKey('companies.id'), nullable=False)
    buy_order_id = db.Column(db.BigInteger, db.ForeignKey('orders.id'), nullable=False)
    sell_order_id = db.Column(db.BigInteger, db.ForeignKey('orders.id'), nullable=False)
    price = db.Column(db.DECIMAL(10, 2), nullable=False)
    quantity = db.Column(db.BigInteger, nullable=False)
    created_at = db.Column(db.TIMESTAMP, nullable=False, default=datetime.utcnow)
    
    # 移除 updated_at 字段的继承
    __mapper_args__ = {
        'exclude_properties': ['updated_at']
    }
    
    def calculate_amount(self):
        """计算成交金额"""
        return float(self.price * self.quantity)
    
    def calculate_fee(self):
        """计算手续费"""
        return float(self.calculate_amount() * Decimal('0.001'))  # 0.1%手续费
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'company_id': self.company_id,
            'buy_order_id': self.buy_order_id,
            'sell_order_id': self.sell_order_id,
            'price': float(self.price),
            'quantity': self.quantity,
            'amount': self.calculate_amount(),
            'fee': self.calculate_fee(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        } 