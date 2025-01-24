from flask import Flask, request, jsonify
import pymysql

app = Flask(__name__)

# 生产环境日志配置
if __name__ != '__main__':
    import logging
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

# 数据库连接配置
def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='cs_aiwanba_net',
        password='sQz9HSnF5ZcXj9SX',
        database='cs_aiwanba_net',
        port=3306,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route('/')
def index():
    return 'Stock Trading Game'

@app.route('/api/trade', methods=['POST'])
def stock_trade():
    """股票交易接口（市价单）"""
    try:
        data = request.json
        required_fields = ['user_id', 'company_id', 'shares', 'type']
        if not all(k in data for k in required_fields):
            return jsonify({'error': 'Missing parameters'}), 400

        # 执行交易逻辑
        result = execute_trade(
            data['user_id'],
            data['company_id'],
            data['shares'],
            data['type']
        )
        return jsonify(result)
    except Exception as e:
        app.logger.error(f"Trade error: {str(e)}")
        return jsonify({'error': str(e)}), 500

def execute_trade(user_id, company_id, shares, trade_type):
    """执行股票交易核心逻辑"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 获取当前股价
            cursor.execute(
                "SELECT current_price FROM companies WHERE id=%s",
                (company_id,)
            )
            company = cursor.fetchone()
            if not company:
                raise ValueError("Company not found")
            
            price = company['current_price']
            total_cost = price * shares

            # 开始事务
            conn.begin()

            # 更新用户余额
            if trade_type == 'BUY':
                cursor.execute(
                    "UPDATE users SET balance = balance - %s WHERE id=%s AND balance >= %s",
                    (total_cost, user_id, total_cost)
                )
            else:
                cursor.execute(
                    "UPDATE users SET balance = balance + %s WHERE id=%s",
                    (total_cost, user_id)
                )

            if cursor.rowcount == 0:
                raise ValueError("Insufficient balance" if trade_type == 'BUY' else "User not found")

            # 记录交易
            cursor.execute(
                """INSERT INTO stock_transactions 
                (user_id, company_id, shares, price, transaction_type)
                VALUES (%s, %s, %s, %s, %s)""",
                (user_id, company_id, shares, price, trade_type)
            )

            conn.commit()
            return {'message': 'Trade executed successfully', 'price': price}
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True) 