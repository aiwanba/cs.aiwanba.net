from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://cs_aiwanba_net:sQz9HSnF5ZcXj9SX@localhost:3306/cs_aiwanba_net'
db = SQLAlchemy(app)

# 公司模型
class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    owner_id = db.Column(db.Integer)
    initial_capital = db.Column(db.Numeric(15, 2), nullable=False)

# 股票交易模型
class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, nullable=False)
    player_id = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(15, 2), nullable=False)
    transaction_type = db.Column(db.Enum('buy', 'sell'), nullable=False)
    transaction_time = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())

# 账户模型
class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, nullable=False)
    balance = db.Column(db.Numeric(15, 2), nullable=False)

# 交易模型
class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, nullable=False)
    transaction_type = db.Column(db.Enum('deposit', 'withdraw', 'transfer'), nullable=False)
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    transaction_time = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())

# AI 玩家模型
class AIPlayer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    strategy = db.Column(db.Enum('conservative', 'aggressive', 'balanced'), nullable=False)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())

# AI 交易模型
class AITransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ai_player_id = db.Column(db.Integer, nullable=False)
    company_id = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(15, 2), nullable=False)
    transaction_type = db.Column(db.Enum('buy', 'sell'), nullable=False)
    transaction_time = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())

# 创建公司
@app.route('/company', methods=['POST'])
def create_company():
    data = request.json
    new_company = Company(
        name=data['name'],
        owner_id=data['owner_id'],
        initial_capital=data['initial_capital']
    )
    db.session.add(new_company)
    db.session.commit()
    return jsonify({'message': 'Company created successfully', 'company_id': new_company.id}), 201

# 获取公司信息
@app.route('/company/<int:company_id>', methods=['GET'])
def get_company(company_id):
    company = Company.query.get_or_404(company_id)
    return jsonify({
        'id': company.id,
        'name': company.name,
        'created_at': company.created_at,
        'owner_id': company.owner_id,
        'initial_capital': float(company.initial_capital)
    })

# 买卖股票
@app.route('/stock', methods=['POST'])
def trade_stock():
    data = request.json
    new_stock = Stock(
        company_id=data['company_id'],
        player_id=data['player_id'],
        quantity=data['quantity'],
        price=data['price'],
        transaction_type=data['transaction_type']
    )
    db.session.add(new_stock)
    db.session.commit()
    return jsonify({'message': 'Stock transaction completed', 'transaction_id': new_stock.id}), 201

# 创建账户
@app.route('/account', methods=['POST'])
def create_account():
    data = request.json
    new_account = Account(
        company_id=data['company_id'],
        balance=data['initial_balance']
    )
    db.session.add(new_account)
    db.session.commit()
    return jsonify({'message': 'Account created successfully', 'account_id': new_account.id}), 201

# 存款
@app.route('/account/deposit', methods=['POST'])
def deposit():
    data = request.json
    account = Account.query.get_or_404(data['account_id'])
    account.balance += data['amount']
    new_transaction = Transaction(
        account_id=data['account_id'],
        transaction_type='deposit',
        amount=data['amount']
    )
    db.session.add(new_transaction)
    db.session.commit()
    return jsonify({'message': 'Deposit successful', 'new_balance': float(account.balance)})

# 取款
@app.route('/account/withdraw', methods=['POST'])
def withdraw():
    data = request.json
    account = Account.query.get_or_404(data['account_id'])
    if account.balance < data['amount']:
        return jsonify({'message': 'Insufficient balance'}), 400
    account.balance -= data['amount']
    new_transaction = Transaction(
        account_id=data['account_id'],
        transaction_type='withdraw',
        amount=data['amount']
    )
    db.session.add(new_transaction)
    db.session.commit()
    return jsonify({'message': 'Withdrawal successful', 'new_balance': float(account.balance)})

# 转账
@app.route('/account/transfer', methods=['POST'])
def transfer():
    data = request.json
    from_account = Account.query.get_or_404(data['from_account_id'])
    to_account = Account.query.get_or_404(data['to_account_id'])
    if from_account.balance < data['amount']:
        return jsonify({'message': 'Insufficient balance'}), 400
    from_account.balance -= data['amount']
    to_account.balance += data['amount']
    new_transaction = Transaction(
        account_id=data['from_account_id'],
        transaction_type='transfer',
        amount=data['amount']
    )
    db.session.add(new_transaction)
    db.session.commit()
    return jsonify({'message': 'Transfer successful', 'new_balance': float(from_account.balance)})

# 查询交易历史
@app.route('/transactions/<int:company_id>', methods=['GET'])
def get_transactions(company_id):
    transactions = Transaction.query.filter_by(account_id=company_id).all()
    result = []
    for transaction in transactions:
        result.append({
            'id': transaction.id,
            'account_id': transaction.account_id,
            'transaction_type': transaction.transaction_type,
            'amount': float(transaction.amount),
            'transaction_time': transaction.transaction_time
        })
    return jsonify(result)

# 创建 AI 玩家
@app.route('/ai_player', methods=['POST'])
def create_ai_player():
    data = request.json
    new_ai_player = AIPlayer(
        name=data['name'],
        strategy=data['strategy']
    )
    db.session.add(new_ai_player)
    db.session.commit()
    return jsonify({'message': 'AI player created successfully', 'ai_player_id': new_ai_player.id}), 201

# 获取 AI 玩家信息
@app.route('/ai_player/<int:ai_player_id>', methods=['GET'])
def get_ai_player(ai_player_id):
    ai_player = AIPlayer.query.get_or_404(ai_player_id)
    return jsonify({
        'id': ai_player.id,
        'name': ai_player.name,
        'strategy': ai_player.strategy,
        'created_at': ai_player.created_at
    })

# AI 玩家进行交易
@app.route('/ai_transaction', methods=['POST'])
def ai_trade():
    data = request.json
    new_ai_transaction = AITransaction(
        ai_player_id=data['ai_player_id'],
        company_id=data['company_id'],
        quantity=data['quantity'],
        price=data['price'],
        transaction_type=data['transaction_type']
    )
    db.session.add(new_ai_transaction)
    db.session.commit()
    return jsonify({'message': 'AI transaction completed', 'transaction_id': new_ai_transaction.id}), 201

# 查询 AI 交易历史
@app.route('/ai_transactions/<int:ai_player_id>', methods=['GET'])
def get_ai_transactions(ai_player_id):
    ai_transactions = AITransaction.query.filter_by(ai_player_id=ai_player_id).all()
    result = []
    for transaction in ai_transactions:
        result.append({
            'id': transaction.id,
            'ai_player_id': transaction.ai_player_id,
            'company_id': transaction.company_id,
            'quantity': transaction.quantity,
            'price': float(transaction.price),
            'transaction_type': transaction.transaction_type,
            'transaction_time': transaction.transaction_time
        })
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5010) 