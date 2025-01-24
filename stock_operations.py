def create_limit_order(user_id, company_id, shares, price, order_type):
    """创建限价单"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 冻结资金或股票
            if order_type == 'BUY':
                total = price * shares
                cursor.execute(
                    "UPDATE users SET balance = balance - %s WHERE id=%s AND balance >= %s",
                    (total, user_id, total)
                )
            else:
                cursor.execute(
                    "SELECT shares FROM user_stocks WHERE user_id=%s AND company_id=%s",
                    (user_id, company_id)
                )
                holding = cursor.fetchone()
                if not holding or holding['shares'] < shares:
                    raise ValueError("Insufficient shares")

            # 创建限价单记录
            cursor.execute("""
                INSERT INTO limit_orders 
                (user_id, company_id, shares, limit_price, order_type)
                VALUES (%s, %s, %s, %s, %s)
            """, (user_id, company_id, shares, price, order_type))
            
            conn.commit()
            
            # 合并检测
            from merger_detector import check_and_process_mergers
            check_and_process_mergers(company_id)
            
            return cursor.lastrowid
    finally:
        conn.close() 