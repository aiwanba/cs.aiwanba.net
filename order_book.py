from database import get_db_connection

def match_orders(company_id: int):
    """限价单匹配引擎"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 获取所有未成交的买单（按价格降序排列）
            cursor.execute("""
                SELECT * FROM limit_orders 
                WHERE company_id=%s 
                AND order_type='BUY' 
                AND status='OPEN'
                ORDER BY limit_price DESC
            """, (company_id,))
            buy_orders = cursor.fetchall()

            # 获取所有未成交的卖单（按价格升序排列）
            cursor.execute("""
                SELECT * FROM limit_orders 
                WHERE company_id=%s 
                AND order_type='SELL' 
                AND status='OPEN'
                ORDER BY limit_price ASC
            """, (company_id,))
            sell_orders = cursor.fetchall()

            # 执行订单匹配逻辑
            for buy_order in buy_orders:
                for sell_order in sell_orders:
                    if buy_order['limit_price'] >= sell_order['limit_price']:
                        execute_limit_trade(
                            buy_order['id'],
                            sell_order['id'],
                            min(buy_order['shares'], sell_order['shares'])
                        )
                        # 更新剩余股数
                        buy_order['shares'] -= traded_shares
                        sell_order['shares'] -= traded_shares
                        if buy_order['shares'] == 0:
                            break
            conn.commit()
    finally:
        conn.close() 