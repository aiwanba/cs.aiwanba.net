from database import get_db_connection
import random

class BaseAIStrategy:
    def __init__(self, ai_id):
        self.ai_id = ai_id
        self.conn = get_db_connection()
        
    def make_decision(self):
        """基础策略决策方法"""
        raise NotImplementedError

class ConservativeStrategy(BaseAIStrategy):
    def make_decision(self):
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT balance FROM ai_players WHERE id=%s", (self.ai_id,))
            balance = cursor.fetchone()['balance']
            # 获取市场平均价格波动
            cursor.execute("""
                SELECT AVG(price) as avg_price, 
                       STD(price) as std_price 
                FROM stock_transactions 
                WHERE created_at >= NOW() - INTERVAL 1 HOUR
            """)
            market = cursor.fetchone()
            volatility = market['std_price'] / market['avg_price'] if market['avg_price'] else 0

            if balance > 50000:
                buy_prob = 0.3 * (1 - volatility)  # 波动越大买入概率越低
                return {'action': 'BUY', 'probability': max(0.1, buy_prob)}
            return {'action': 'HOLD', 'probability': 0.7 * (1 + volatility)}

class AggressiveStrategy(BaseAIStrategy):
    def make_decision(self):
        return {'action': 'BUY' if random.random() > 0.5 else 'SELL', 'probability': 0.8}

class BalancedStrategy(BaseAIStrategy):
    def make_decision(self):
        return {'action': 'HOLD', 'probability': 0.6}

def execute_strategy(ai_id: int):
    """执行AI策略并记录操作"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 获取AI策略类型
            cursor.execute("SELECT strategy_type FROM ai_players WHERE id=%s", (ai_id,))
            strategy_type = cursor.fetchone()['strategy_type']
            
            # 实例化策略
            strategy = {
                'CONSERVATIVE': ConservativeStrategy,
                'AGGRESSIVE': AggressiveStrategy,
                'BALANCED': BalancedStrategy
            }[strategy_type](ai_id)
            
            decision = strategy.make_decision()
            
            # 记录操作
            cursor.execute("""
                INSERT INTO ai_actions 
                (ai_id, action_type) 
                VALUES (%s, %s)
            """, (ai_id, decision['action']))
            
            conn.commit()
            return decision
    finally:
        conn.close() 