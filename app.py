from flask import Flask, render_template, request, redirect, url_for
from models.company import Company
from models.stock import Stock
from models.exchange import Exchange
from models.bank import Bank
from models.ai_company import AICompany
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 添加sum函数到Jinja2环境
app.jinja_env.globals.update(sum=sum)

# 初始化一些示例数据
exchange = Exchange()
bank = Bank("Main Bank", 1000000000)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/companies')
def list_companies():
    # 这里可以显示所有公司
    return render_template('companies.html')

@app.route('/company/<int:company_id>')
def company_detail(company_id):
    # 显示公司详情
    return render_template('company_detail.html', company_id=company_id)

@app.route('/stock/<int:stock_id>')
def stock_detail(stock_id):
    # 显示股票详情
    return render_template('stock_detail.html', stock_id=stock_id)

@app.route('/exchange')
def exchange_info():
    # 显示交易所信息
    market_cap = exchange.calculate_market_cap()
    top_companies = exchange.get_top_companies()
    return render_template('exchange.html', 
                          market_cap=market_cap,
                          top_companies=top_companies)

@app.route('/bank')
def bank_info():
    # 显示银行信息
    return render_template('bank.html', bank=bank)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5010) 