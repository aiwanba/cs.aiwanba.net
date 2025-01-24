from flask import Flask, request, jsonify
from database import get_db_connection
from bank_operations import handle_bank_operation
from fee_calculator import calculate_fee
from analysis_operations import get_trade_analysis
from order_manager import cancel_order

app = Flask(__name__)

# 生产环境日志配置
if __name__ != '__main__':
    import logging
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

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

@app.route('/api/bank', methods=['POST'])
def bank_operation():
    """银行系统接口（存款/取款）"""
    try:
        data = request.json
        required_fields = ['user_id', 'amount', 'operation_type']
        if not all(k in data for k in required_fields):
            return jsonify({'error': 'Missing parameters'}), 400

        result = handle_bank_operation(
            data['user_id'],
            data['amount'],
            data['operation_type']
        )
        return jsonify(result)
    except Exception as e:
        app.logger.error(f"Bank error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/limit_order', methods=['POST'])
def create_limit_order():
    """创建限价单接口"""
    try:
        data = request.json
        required_fields = ['user_id', 'company_id', 'shares', 'price', 'type']
        if not all(k in data for k in required_fields):
            return jsonify({'error': 'Missing parameters'}), 400

        # 创建限价单
        order_id = create_limit_order(
            data['user_id'],
            data['company_id'],
            data['shares'],
            data['price'],
            data['type']
        )
        return jsonify({'order_id': order_id})
    except Exception as e:
        app.logger.error(f"Limit order error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/analysis/trades', methods=['GET'])
def trade_analysis():
    """交易历史分析接口"""
    try:
        company_id = request.args.get('company_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not all([company_id, start_date, end_date]):
            return jsonify({'error': 'Missing parameters'}), 400

        data = get_trade_analysis(company_id, start_date, end_date)
        return jsonify({'analysis': data})
    except Exception as e:
        app.logger.error(f"Analysis error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/order/<int:order_id>', methods=['DELETE'])
def cancel_order_endpoint(order_id):
    """订单撤销接口"""
    try:
        user_id = request.json.get('user_id')
        if not user_id:
            return jsonify({'error': 'Missing user_id'}), 400
            
        success = cancel_order(order_id, user_id)
        if success:
            return jsonify({'message': 'Order cancelled successfully'})
        return jsonify({'error': 'Order cancellation failed'}), 400
    except Exception as e:
        app.logger.error(f"Order cancellation error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai', methods=['POST'])
def create_ai_player():
    """创建AI玩家接口"""
    try:
        data = request.json
        strategy = data.get('strategy', 'BALANCED')
        
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO ai_players (strategy_type)
                VALUES (%s)
            """, (strategy,))
            ai_id = cursor.lastrowid
            conn.commit()
            return jsonify({'ai_id': ai_id})
    except Exception as e:
        app.logger.error(f"AI creation error: {str(e)}")
        return jsonify({'error': str(e)}), 500

def execute_trade(user_id, company_id, shares, trade_type):
    """执行股票交易核心逻辑"""
    app.logger.debug(f"尝试交易：用户{user_id} 公司{company_id} 数量{shares} 类型{trade_type}")
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 获取当前股价
            cursor.execute(
                "SELECT current_price FROM companies WHERE id=%s",
                (company_id,)
            )
            company = cursor.fetchone()
            app.logger.debug(f"查询公司结果：{company}")
            if not company:
                raise ValueError("Company not found")
            
            price = company['current_price']
            total_cost = price * shares
            fee = calculate_fee(total_cost)
            total_cost += fee

            # 开始事务
            conn.begin()

            # 更新用户余额
            if trade_type == 'BUY':
                cursor.execute(
                    "UPDATE users SET balance = balance - %s - %s WHERE id=%s AND balance >= %s + %s",
                    (total_cost, fee, user_id, total_cost, fee)
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
    # 开发服务器配置（仅用于测试）
    app.run(
        debug=True, 
        port=5000,  # 开发端口5000 
        host='0.0.0.0'  # 允许外部访问
    ) 