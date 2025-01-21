from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import random
import threading
import time
from sqlalchemy import text

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

# 股票持有模型
class StockHolding(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    target_company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)

# 贷款模型
class Loan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    interest_rate = db.Column(db.Float, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.Enum('active', 'paid'), nullable=False)

# AI策略模型
class AIStrategy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    parameters = db.Column(db.JSON)
    performance = db.Column(db.Float)
    status = db.Column(db.Enum('active', 'inactive'), nullable=False)

# 公司业绩报表模型
class CompanyReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    revenue = db.Column(db.Float, nullable=False)
    profit = db.Column(db.Float, nullable=False)
    assets = db.Column(db.Float, nullable=False)
    liabilities = db.Column(db.Float, nullable=False)
    report_date = db.Column(db.Date, nullable=False)

# 市场行情模型
class MarketData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    open_price = db.Column(db.Float, nullable=False)
    close_price = db.Column(db.Float, nullable=False)
    high_price = db.Column(db.Float, nullable=False)
    low_price = db.Column(db.Float, nullable=False)
    volume = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date, nullable=False)

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
        # 检查买方余额是否足够
        buyer = Company.query.get(data['company_id'])
        if not buyer or buyer.balance < data['quantity'] * data['price']:
            return jsonify({"error": "Insufficient balance"}), 400

        # 创建或更新持股记录
        holding = StockHolding.query.filter_by(
            company_id=data['company_id'],
            target_company_id=data['target_company_id']
        ).first()
        
        if not holding:
            holding = StockHolding(
                company_id=data['company_id'],
                target_company_id=data['target_company_id'],
                quantity=data['quantity']
            )
            db.session.add(holding)
        else:
            holding.quantity += data['quantity']

        # 更新买方余额
        buyer.balance -= data['quantity'] * data['price']

        # 创建交易记录
        new_transaction = Transaction(
            company_id=data['company_id'],
            target_company_id=data['target_company_id'],
            quantity=data['quantity'],
            price=data['price'],
            transaction_type='buy'
        )
        db.session.add(new_transaction)
        db.session.commit()
        return jsonify({"message": "Stock bought successfully"}), 201
    except Exception as e:
        print(f"Error buying stock: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@app.route('/api/transactions/sell', methods=['POST'])
def sell_stock():
    try:
        data = request.get_json()
        # 检查是否持有足够的股票
        holding = StockHolding.query.filter_by(
            company_id=data['company_id'],
            target_company_id=data['target_company_id']
        ).first()
        
        if not holding or holding.quantity < data['quantity']:
            return jsonify({"error": "Insufficient stock"}), 400

        # 更新持股记录
        holding.quantity -= data['quantity']

        # 更新卖方余额
        seller = Company.query.get(data['company_id'])
        seller.balance += data['quantity'] * data['price']

        # 创建交易记录
        new_transaction = Transaction(
            company_id=data['company_id'],
            target_company_id=data['target_company_id'],
            quantity=data['quantity'],
            price=data['price'],
            transaction_type='sell'
        )
        db.session.add(new_transaction)
        db.session.commit()
        return jsonify({"message": "Stock sold successfully"}), 201
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
        # 获取所有 AI 公司和非 AI 公司
        ai_companies = Company.query.filter_by(is_ai=True).all()
        other_companies = Company.query.filter_by(is_ai=False).all()

        for ai_company in ai_companies:
            # 分析每个公司的表现
            for target_company in other_companies:
                # 获取目标公司的历史交易数据
                recent_transactions = Transaction.query.filter_by(
                    target_company_id=target_company.id
                ).order_by(Transaction.transaction_date.desc()).limit(10).all()

                # 计算平均价格趋势
                if recent_transactions:
                    avg_price = sum(t.price for t in recent_transactions) / len(recent_transactions)
                    latest_price = recent_transactions[0].price

                    # 如果当前价格低于平均价格，考虑买入
                    if latest_price < avg_price and ai_company.balance > latest_price * 10:
                        new_transaction = Transaction(
                            company_id=ai_company.id,
                            target_company_id=target_company.id,
                            quantity=10,
                            price=latest_price,
                            transaction_type='buy'
                        )
                        db.session.add(new_transaction)
                        ai_company.balance -= latest_price * 10

                    # 如果当前价格高于平均价格，考虑卖出
                    elif latest_price > avg_price:
                        holding = StockHolding.query.filter_by(
                            company_id=ai_company.id,
                            target_company_id=target_company.id
                        ).first()
                        
                        if holding and holding.quantity > 0:
                            sell_quantity = min(holding.quantity, 5)
                            new_transaction = Transaction(
                                company_id=ai_company.id,
                                target_company_id=target_company.id,
                                quantity=sell_quantity,
                                price=latest_price,
                                transaction_type='sell'
                            )
                            db.session.add(new_transaction)
                            ai_company.balance += latest_price * sell_quantity
                            holding.quantity -= sell_quantity

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

# 贷款相关 API
@app.route('/api/bank/loan', methods=['POST'])
def apply_loan():
    try:
        data = request.get_json()
        company = Company.query.get(data['company_id'])
        if not company:
            return jsonify({"error": "Company not found"}), 404

        # 计算利率（示例：基础利率 5%）
        interest_rate = 5.0
        
        new_loan = Loan(
            company_id=data['company_id'],
            amount=data['amount'],
            interest_rate=interest_rate,
            start_date=db.func.current_date(),
            end_date=db.func.date_add(db.func.current_date(), 
                                    text(f'INTERVAL {data["duration"]} MONTH')),
            status='active'
        )
        
        # 更新公司余额
        company.balance += data['amount']
        
        db.session.add(new_loan)
        db.session.commit()
        return jsonify({"message": "Loan approved"}), 201
    except Exception as e:
        print(f"Error applying for loan: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@app.route('/api/bank/loan/<int:loan_id>/repay', methods=['POST'])
def repay_loan(loan_id):
    try:
        loan = Loan.query.get(loan_id)
        if not loan:
            return jsonify({"error": "Loan not found"}), 404
        
        company = Company.query.get(loan.company_id)
        if not company:
            return jsonify({"error": "Company not found"}), 404
            
        # 计算需要还款的总额（本金 + 利息）
        total_amount = loan.amount * (1 + loan.interest_rate / 100)
        
        if company.balance < total_amount:
            return jsonify({"error": "Insufficient balance"}), 400
            
        company.balance -= total_amount
        loan.status = 'paid'
        
        db.session.commit()
        return jsonify({"message": "Loan repaid successfully"}), 200
    except Exception as e:
        print(f"Error repaying loan: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@app.route('/api/bank/loans', methods=['GET'])
def get_loans():
    try:
        loans = Loan.query.all()
        return jsonify([{
            "id": loan.id,
            "company_id": loan.company_id,
            "amount": loan.amount,
            "interest_rate": loan.interest_rate,
            "start_date": loan.start_date,
            "end_date": loan.end_date,
            "status": loan.status
        } for loan in loans])
    except Exception as e:
        print(f"Error fetching loans: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

# 公司业绩报表 API
@app.route('/api/companies/<int:company_id>/report', methods=['GET'])
def get_company_report(company_id):
    try:
        company = Company.query.get(company_id)
        if not company:
            return jsonify({"error": "Company not found"}), 404
            
        # 获取最新的业绩报表
        report = CompanyReport.query.filter_by(
            company_id=company_id
        ).order_by(CompanyReport.report_date.desc()).first()
        
        if not report:
            # 如果没有报表，生成一个新的
            report = CompanyReport(
                company_id=company_id,
                revenue=0,  # 这里需要根据实际业务逻辑计算
                profit=0,
                assets=company.balance,  # 简单示例：资产等于余额
                liabilities=0,
                report_date=db.func.current_date()
            )
            db.session.add(report)
            db.session.commit()
            
        return jsonify({
            "revenue": report.revenue,
            "profit": report.profit,
            "assets": report.assets,
            "liabilities": report.liabilities,
            "report_date": report.report_date
        })
    except Exception as e:
        print(f"Error getting company report: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

# 市场行情 API
@app.route('/api/market/kline/<int:company_id>', methods=['GET'])
def get_kline_data(company_id):
    try:
        # 获取最近30天的K线数据
        market_data = MarketData.query.filter_by(
            company_id=company_id
        ).order_by(MarketData.date.desc()).limit(30).all()
        
        return jsonify([{
            "date": data.date,
            "open": data.open_price,
            "close": data.close_price,
            "high": data.high_price,
            "low": data.low_price,
            "volume": data.volume
        } for data in market_data])
    except Exception as e:
        print(f"Error getting kline data: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5010, debug=True) 