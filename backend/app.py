from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

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

# 交易模型
class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    stock_symbol = db.Column(db.String(10), nullable=False)
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
        return jsonify([{"id": transaction.id, "company_id": transaction.company_id, "stock_symbol": transaction.stock_symbol, "quantity": transaction.quantity, "price": transaction.price, "transaction_type": transaction.transaction_type, "transaction_date": transaction.transaction_date} for transaction in transactions])
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
            stock_symbol=data['stock_symbol'],
            quantity=data['quantity'],
            price=data['price'],
            transaction_type='buy'
        )
        db.session.add(new_transaction)
        db.session.commit()
        return jsonify({"id": new_transaction.id, "company_id": new_transaction.company_id, "stock_symbol": new_transaction.stock_symbol, "quantity": new_transaction.quantity, "price": new_transaction.price, "transaction_type": new_transaction.transaction_type, "transaction_date": new_transaction.transaction_date}), 201
    except Exception as e:
        print(f"Error buying stock: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@app.route('/api/transactions/sell', methods=['POST'])
def sell_stock():
    try:
        data = request.get_json()
        new_transaction = Transaction(
            company_id=data['company_id'],
            stock_symbol=data['stock_symbol'],
            quantity=data['quantity'],
            price=data['price'],
            transaction_type='sell'
        )
        db.session.add(new_transaction)
        db.session.commit()
        return jsonify({"id": new_transaction.id, "company_id": new_transaction.company_id, "stock_symbol": new_transaction.stock_symbol, "quantity": new_transaction.quantity, "price": new_transaction.price, "transaction_type": new_transaction.transaction_type, "transaction_date": new_transaction.transaction_date}), 201
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
        # 示例：根据市场数据自动买入或卖出股票
        # 这里可以添加更复杂的逻辑，例如使用机器学习模型
        pass
    except Exception as e:
        print(f"Error in AI trade: {e}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5010, debug=True) 