from database import get_db_connection

def cancel_order(order_id: int, user_id: int):
    """撤销限价单核心逻辑"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 获取订单详情
            cursor.execute("""
                SELECT * FROM limit_orders 
                WHERE id = %s AND user_id = %s 
                AND status = 'OPEN'
            """, (order_id, user_id))
            order = cursor.fetchone()
            
            if not order:
                raise ValueError("Order not found or not cancellable")
            
            # 恢复资金或股票
            if order['order_type'] == 'BUY':
                cursor.execute("""
                    UPDATE users 
                    SET balance = balance + %s 
                    WHERE id = %s
                """, (order['limit_price'] * order['shares'], user_id))
            else:
                cursor.execute("""
                    UPDATE user_stocks 
                    SET shares = shares + %s 
                    WHERE user_id = %s AND company_id = %s
                """, (order['shares'], user_id, order['company_id']))
            
            # 更新订单状态
            cursor.execute("""
                UPDATE limit_orders 
                SET status = 'CANCELLED' 
                WHERE id = %s
            """, (order_id,))
            
            # 记录撤销操作
            cursor.execute("""
                INSERT INTO order_cancellations 
                (order_id, reason) 
                VALUES (%s, 'USER_REQUEST')
            """, (order_id,))
            
            conn.commit()
            return True
    finally:
        conn.close() 