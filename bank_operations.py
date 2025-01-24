import pymysql
from database import get_db_connection

def handle_bank_operation(user_id, amount, operation_type):
    """处理银行操作核心逻辑"""
    if operation_type not in ('DEPOSIT', 'WITHDRAW'):
        raise ValueError("Invalid operation type")
    
    if amount <= 0:
        raise ValueError("Amount must be positive")

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 开始事务
            conn.begin()

            # 更新余额
            if operation_type == 'DEPOSIT':
                cursor.execute(
                    "UPDATE users SET balance = balance + %s WHERE id=%s",
                    (amount, user_id)
                )
            else:
                cursor.execute(
                    "UPDATE users SET balance = balance - %s WHERE id=%s AND balance >= %s",
                    (amount, user_id, amount)
                )

            if cursor.rowcount == 0:
                raise ValueError("Operation failed: Insufficient balance" if operation_type == 'WITHDRAW' else "User not found")

            # 记录交易
            cursor.execute(
                """INSERT INTO bank_transactions 
                (user_id, amount, operation_type)
                VALUES (%s, %s, %s)""",
                (user_id, amount, operation_type)
            )

            conn.commit()
            return {'message': 'Operation successful'}
    finally:
        conn.close() 