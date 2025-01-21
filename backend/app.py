from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import random
import threading
import time

app = Flask(__name__)
CORS(app)  # 启用 CORS

# 数据库配置
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://cs_aiwanba_net:sQz9HSnF5ZcXj9SX@localhost:3306/cs_aiwanba_net'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 公司模型
class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    balance = db.Column(db.Float, nullable=False)
    is_ai = db.Column(db.Boolean, nullable=False, default=False)

# 交易模型
class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    asset_type = db.Column(db.Enum('stock', 'futures', 'forex'), nullable=False, default='stock')
    target_company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    transaction_type = db.Column(db.Enum('buy', 'sell'), nullable=False)
    transaction_date = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())

@app.route('/')
def index():
    return jsonify({"message": "Welcome to the Stock Trading Game!"})

@app.route('/api/companies', methods=['GET'])
def get_companies():
    try:
        companies = Company.query.all()
        return jsonify([{"id": company.id, "name": company.name, "balance": company.balance} for company in companies])
    except Exception as e:
        print(f"Error fetching companies: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    try:
        transactions = Transaction.query.all()
        return jsonify([{
            "id": transaction.id, 
            "company_id": transaction.company_id,
            "target_company_id": transaction.target_company_id,
            "asset_type": transaction.asset_type,
            "quantity": transaction.quantity,
            "price": transaction.price,
            "transaction_type": transaction.transaction_type,
            "transaction_date": transaction.transaction_date
        } for transaction in transactions])
    except Exception as e:
        print(f"Error fetching transactions: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@app.route('/api/companies', methods=['POST'])
def create_company():
    try:
        data = request.get_json()
        new_company = Company(name=data['name'], balance=data['balance'])
        db.session.add(new_company)
        db.session.commit()
        return jsonify({"id": new_company.id, "name": new_company.name, "balance": new_company.balance}), 201
    except Exception as e:
        print(f"Error creating company: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@app.route('/api/companies/<int:company_id>', methods=['PUT'])
def update_company(company_id):
    try:
        data = request.get_json()
        company = Company.query.get(company_id)
        if company:
            company.name = data.get('name', company.name)
            company.balance = data.get('balance', company.balance)
            db.session.commit()
            return jsonify({"id": company.id, "name": company.name, "balance": company.balance})
        else:
            return jsonify({"error": "Company not found"}), 404
    except Exception as e:
        print(f"Error updating company: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@app.route('/api/companies/<int:company_id>', methods=['DELETE'])
def delete_company(company_id):
    try:
        company = Company.query.get(company_id)
        if company:
            db.session.delete(company)
            db.session.commit()
            return jsonify({"message": "Company deleted"})
        else:
            return jsonify({"error": "Company not found"}), 404
    except Exception as e:
        print(f"Error deleting company: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@app.route('/api/transactions/buy', methods=['POST'])
def buy_stock():
    try:
        data = request.get_json()
        new_transaction = Transaction(
            company_id=data['company_id'],
            target_company_id=data['target_company_id'],
            quantity=data['quantity'],
            price=data['price'],
            transaction_type='buy'
        )
        db.session.add(new_transaction)
        db.session.commit()
        return jsonify({"id": new_transaction.id, "company_id": new_transaction.company_id, "target_company_id": new_transaction.target_company_id, "quantity": new_transaction.quantity, "price": new_transaction.price, "transaction_type": new_transaction.transaction_type, "transaction_date": new_transaction.transaction_date}), 201
    except Exception as e:
        print(f"Error buying stock: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@app.route('/api/transactions/sell', methods=['POST'])
def sell_stock():
    try:
        data = request.get_json()
        new_transaction = Transaction(
            company_id=data['company_id'],
            target_company_id=data['target_company_id'],
            quantity=data['quantity'],
            price=data['price'],
            transaction_type='sell'
        )
        db.session.add(new_transaction)
        db.session.commit()
        return jsonify({"id": new_transaction.id, "company_id": new_transaction.company_id, "target_company_id": new_transaction.target_company_id, "quantity": new_transaction.quantity, "price": new_transaction.price, "transaction_type": new_transaction.transaction_type, "transaction_date": new_transaction.transaction_date}), 201
    except Exception as e:
        print(f"Error selling stock: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@app.route('/api/bank/deposit', methods=['POST'])
def deposit():
    try:
        data = request.get_json()
        company = Company.query.get(data['company_id'])
        if company:
            company.balance += data['amount']
            db.session.commit()
            return jsonify({"id": company.id, "name": company.name, "balance": company.balance})
        else:
            return jsonify({"error": "Company not found"}), 404
    except Exception as e:
        print(f"Error depositing: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@app.route('/api/bank/withdraw', methods=['POST'])
def withdraw():
    try:
        data = request.get_json()
        company = Company.query.get(data['company_id'])
        if company:
            if company.balance >= data['amount']:
                company.balance -= data['amount']
                db.session.commit()
                return jsonify({"id": company.id, "name": company.name, "balance": company.balance})
            else:
                return jsonify({"error": "Insufficient balance"}), 400
        else:
            return jsonify({"error": "Company not found"}), 404
    except Exception as e:
        print(f"Error withdrawing: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@app.route('/api/bank/transfer', methods=['POST'])
def transfer():
    try:
        data = request.get_json()
        from_company = Company.query.get(data['from_company_id'])
        to_company = Company.query.get(data['to_company_id'])
        if from_company and to_company:
            if from_company.balance >= data['amount']:
                from_company.balance -= data['amount']
                to_company.balance += data['amount']
                db.session.commit()
                return jsonify({"from_company": {"id": from_company.id, "name": from_company.name, "balance": from_company.balance}, "to_company": {"id": to_company.id, "name": to_company.name, "balance": to_company.balance}})
            else:
                return jsonify({"error": "Insufficient balance"}), 400
        else:
            return jsonify({"error": "Company not found"}), 404
    except Exception as e:
        print(f"Error transferring: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

# AI 交易逻辑
def ai_trade():
    try:
        # 获取所有 AI 公司
        ai_companies = Company.query.filter_by(is_ai=True).all()
        for company in ai_companies:
            # 示例：如果公司余额大于 1000，则买入股票
            if company.balance > 1000:
                # 买入股票
                new_transaction = Transaction(
                    company_id=company.id,
                    target_company_id=company.id,  # 买入股票到自己公司
                    quantity=10,         # 买入数量
                    price=150,           # 买入价格
                    transaction_type='buy'
                )
                db.session.add(new_transaction)
                company.balance -= 10 * 150  # 更新公司余额
            # 示例：如果公司余额小于 500，则卖出股票
            elif company.balance < 500:
                # 卖出股票
                new_transaction = Transaction(
                    company_id=company.id,
                    target_company_id=company.id,  # 卖出股票到自己公司
                    quantity=5,          # 卖出数量
                    price=150,           # 卖出价格
                    transaction_type='sell'
                )
                db.session.add(new_transaction)
                company.balance += 5 * 150  # 更新公司余额
        db.session.commit()
    except Exception as e:
        print(f"Error in AI trade: {e}")

# 模拟市场数据
def simulate_market_data():
    try:
        # 示例：模拟股票价格波动
        transactions = Transaction.query.all()
        for transaction in transactions:
            if transaction.asset_type == 'stock':
                # 示例：股票价格随机波动
                transaction.price += (transaction.price * 0.01 * (random.random() - 0.5))
        db.session.commit()
    except Exception as e:
        print(f"Error simulating market data: {e}")

# 定时任务：每 10 秒执行一次 AI 交易和市场数据模拟
def background_tasks():
    while True:
        ai_trade()
        simulate_market_data()
        time.sleep(10)

# 启动后台任务
thread = threading.Thread(target=background_tasks)
thread.daemon = True
thread.start()

# 初始化 AI 公司
def initialize_ai_company():
    try:
        ai_company = Company.query.filter_by(is_ai=True).first()
        if not ai_company:
            ai_company = Company(name="AI 公司", balance=10000, is_ai=True)
            db.session.add(ai_company)
            db.session.commit()
    except Exception as e:
        print(f"Error initializing AI company: {e}")

# 在应用启动时调用
initialize_ai_company()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5010, debug=True) 