from flask import Blueprint, request, jsonify
from models.bank import BankAccount, TimeDeposit, StockPledgeLoan
from models.company import Company
from models.shareholder import Shareholder
from models import db
from datetime import datetime, timedelta

bank_bp = Blueprint('bank', __name__)

@bank_bp.route('/api/bank/account', methods=['POST'])
def create_account():
    """创建银行账户"""
    try:
        user_id = request.user_id  # 假设通过认证中间件设置
        
        # 检查是否已有账户
        existing_account = BankAccount.query.filter_by(user_id=user_id).first()
        if existing_account:
            return jsonify({'error': 'Account already exists'}), 400
            
        account = BankAccount(user_id=user_id)
        db.session.add(account)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'account': account.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bank_bp.route('/api/bank/deposit', methods=['POST'])
def create_deposit():
    """创建定期存款"""
    try:
        data = request.get_json()
        if 'amount' not in data:
            return jsonify({'error': 'Missing amount'}), 400
            
        user_id = request.user_id
        account = BankAccount.query.filter_by(user_id=user_id).first_or_404()
        
        # 检查余额
        if account.balance < data['amount']:
            return jsonify({'error': 'Insufficient balance'}), 400
            
        # 创建7天定期存款
        deposit = TimeDeposit(
            user_id=user_id,
            amount=data['amount'],
            interest_rate=0.0001,  # 0.01% 日利率
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=7)
        )
        
        # 扣除活期余额
        account.balance -= data['amount']
        
        db.session.add(deposit)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Time deposit created successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bank_bp.route('/api/bank/loan', methods=['POST'])
def create_loan():
    """创建股票质押贷款"""
    try:
        data = request.get_json()
        required_fields = ['company_id', 'shares']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400
                
        user_id = request.user_id
        company = Company.query.get_or_404(data['company_id'])
        
        # 检查持股数量
        shareholder = Shareholder.query.filter_by(
            company_id=data['company_id'],
            user_id=user_id
        ).first_or_404()
        
        if shareholder.shares < data['shares']:
            return jsonify({'error': 'Insufficient shares'}), 400
            
        # 计算贷款金额（股票市值的50%）
        loan_amount = company.stock_price * data['shares'] * 0.5
        
        # 创建贷款
        loan = StockPledgeLoan(
            user_id=user_id,
            company_id=data['company_id'],
            pledged_shares=data['shares'],
            loan_amount=loan_amount
        )
        
        # 更新股东持股记录（质押股票）
        shareholder.shares -= data['shares']
        
        # 增加用户现金
        account = BankAccount.query.filter_by(user_id=user_id).first()
        if account:
            account.balance += loan_amount
        else:
            account = BankAccount(user_id=user_id, balance=loan_amount)
            db.session.add(account)
        
        db.session.add(loan)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'loan_amount': loan_amount
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bank_bp.route('/api/bank/account/balance', methods=['GET'])
def get_balance():
    """查询账户余额"""
    user_id = request.user_id
    account = BankAccount.query.filter_by(user_id=user_id).first_or_404()
    
    # 获取定期存款信息
    deposits = TimeDeposit.query.filter_by(
        user_id=user_id,
        status='active'
    ).all()
    
    # 获取贷款信息
    loans = StockPledgeLoan.query.filter_by(
        user_id=user_id,
        status='active'
    ).all()
    
    return jsonify({
        'balance': account.balance,
        'time_deposits': [{
            'amount': d.amount,
            'end_date': d.end_date.isoformat()
        } for d in deposits],
        'loans': [{
            'amount': l.loan_amount,
            'pledged_shares': l.pledged_shares
        } for l in loans]
    }) 