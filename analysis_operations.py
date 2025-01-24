from database import get_db_connection

def get_trade_analysis(company_id: int, start_date: str, end_date: str):
    """获取指定公司交易分析"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT * FROM trade_analysis_view
                WHERE company_id = %s
                AND trade_date BETWEEN %s AND %s
                ORDER BY trade_date DESC
            """, (company_id, start_date, end_date))
            return cursor.fetchall()
    finally:
        conn.close() 