import schedule
import time
from ai_strategies import execute_strategy
from database import get_db_connection

def run_ai_trading():
    """执行所有AI玩家的交易策略"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM ai_players")
            ai_players = cursor.fetchall()
            for ai in ai_players:
                try:
                    execute_strategy(ai['id'])
                except Exception as e:
                    print(f"AI {ai['id']} 执行失败: {str(e)}")
    finally:
        conn.close()

# 每5分钟执行一次
schedule.every(5).minutes.do(run_ai_trading)

if __name__ == '__main__':
    while True:
        schedule.run_pending()
        time.sleep(1) 