from database import get_db_connection

def check_and_process_mergers(company_id: int):
    """检测并处理公司合并"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 获取该公司所有持股情况
            cursor.execute("""
                SELECT target_company_id, shares_held 
                FROM company_holdings
                WHERE holder_company_id = %s
            """, (company_id,))
            holdings = cursor.fetchall()
            
            for holding in holdings:
                target_id = holding['target_company_id']
                # 获取目标公司总股本
                cursor.execute("""
                    SELECT total_shares FROM companies WHERE id = %s
                """, (target_id,))
                total_shares = cursor.fetchone()['total_shares']
                
                # 判断是否达到80%持股
                if holding['shares_held'] / total_shares >= 0.8:
                    execute_merger(company_id, target_id, cursor)
            
            conn.commit()
    finally:
        conn.close()

def execute_merger(acquirer_id: int, target_id: int, cursor):
    """执行公司合并"""
    try:
        # 1. 转移所有资产
        cursor.execute("""
            UPDATE companies 
            SET total_shares = total_shares + (
                SELECT total_shares FROM companies WHERE id = %s
            )
            WHERE id = %s
        """, (target_id, acquirer_id))
        
        # 2. 转移股票持有关系
        cursor.execute("""
            UPDATE company_holdings
            SET holder_company_id = %s
            WHERE holder_company_id = %s
        """, (acquirer_id, target_id))
        
        # 3. 标记目标公司为已合并
        cursor.execute("""
            UPDATE companies 
            SET current_price = 0, 
                status = 'MERGED'
            WHERE id = %s
        """, (target_id,))
        
        # 4. 记录合并事件
        cursor.execute("""
            INSERT INTO merger_events 
            (acquirer_id, target_id, merger_date)
            VALUES (%s, %s, NOW())
        """, (acquirer_id, target_id))
    except Exception as e:
        # 回滚事务
        cursor.connection.rollback()
        raise e 