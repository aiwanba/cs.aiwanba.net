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
            if balance > 50000:
                return {'action': 'BUY', 'probability': 0.3}
            return {'action': 'HOLD', 'probability': 0.7}

class AggressiveStrategy(BaseAIStrategy):
    def make_decision(self):
        return {'action': 'BUY' if random.random() > 0.5 else 'SELL', 'probability': 0.8}

class BalancedStrategy(BaseAIStrategy):
    def make_decision(self):
        return {'action': 'HOLD', 'probability': 0.6} 