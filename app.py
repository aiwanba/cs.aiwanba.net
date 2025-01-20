from flask import Flask, render_template, request, redirect, url_for
from extensions import db
from dotenv import load_dotenv
import os

load_dotenv()  # 加载环境变量

app = Flask(__name__)

# 数据库配置
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'mysql+pymysql://cs_aiwanba_net:sQz9HSnF5ZcXj9SX@localhost:3306/cs_aiwanba_net')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化数据库
db.init_app(app)

# 在db初始化之后导入模型
from models import Company, Stock, Exchange, Bank, AICompany

# 创建数据库表
def initialize_database():
    with app.app_context():
        try:
            db.create_all()
            print("数据库表已成功创建")
        except Exception as e:
            print(f"数据库初始化失败: {str(e)}")
            # 可以根据需要添加重试逻辑或退出应用

# 初始化数据库
initialize_database()

# 添加sum函数到Jinja2环境
app.jinja_env.globals.update(sum=sum)

# 初始化一些示例数据
exchange = Exchange()
bank = Bank(name="Main Bank", capital=1000000000)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/companies')
def list_companies():
    search = request.args.get('search', '')
    industry = request.args.get('industry', '')
    page = request.args.get('page', 1, type=int)
    per_page = 10

    query = Company.query
    if search:
        query = query.filter(Company.name.contains(search))
    if industry:
        query = query.filter_by(industry=industry)

    companies = query.paginate(page=page, per_page=per_page)
    return render_template('companies.html', companies=companies)

@app.route('/company/<int:company_id>')
def company_detail(company_id):
    company = Company.query.get_or_404(company_id)
    return render_template('company_detail.html', company=company)

@app.route('/stock/<int:stock_id>')
def stock_detail(stock_id):
    # 显示股票详情
    return render_template('stock_detail.html', stock_id=stock_id)

@app.route('/exchange')
def exchange_info():
    # 获取所有上市公司
    listed_companies = Company.query.filter(Company.stock_count > 0).all()
    
    # 计算总市值
    market_cap = sum(company.capital for company in listed_companies)
    
    # 获取市值排名前5的公司
    top_companies = sorted(listed_companies, 
                          key=lambda c: c.capital, 
                          reverse=True)[:5]
    
    # 计算市场指数（示例）
    market_index = market_cap / 1000000  # 假设以百万为单位
    
    return render_template('exchange.html', 
                          market_cap=market_cap,
                          market_index=market_index,
                          top_companies=top_companies,
                          listed_companies=listed_companies)

@app.route('/bank')
def bank_info():
    # 显示银行信息
    return render_template('bank.html', bank=bank)

@app.route('/create_company', methods=['GET', 'POST'])
def create_company():
    if request.method == 'POST':
        name = request.form.get('name')
        industry = request.form.get('industry')
        capital = float(request.form.get('capital'))
        
        new_company = Company(name=name, industry=industry, capital=capital)
        db.session.add(new_company)
        db.session.commit()
        
        return redirect(url_for('list_companies'))
    return render_template('create_company.html')

@app.route('/list_company', methods=['POST'])
def list_company():
    # 处理公司上市逻辑
    company_id = request.form.get('company_id')
    # 实现公司上市逻辑
    return redirect(url_for('exchange_info'))

@app.route('/loan', methods=['POST'])
def loan():
    # 处理贷款逻辑
    company_id = request.form.get('company_id')
    amount = float(request.form.get('amount'))
    # 实现贷款逻辑
    return redirect(url_for('bank_info'))

@app.route('/delist_company', methods=['POST'])
def delist_company():
    # 处理公司退市逻辑
    company_id = request.form.get('company_id')
    # 实现公司退市逻辑
    return redirect(url_for('exchange_info'))

@app.route('/deposit', methods=['POST'])
def deposit():
    # 处理存款逻辑
    company_id = request.form.get('company_id')
    amount = float(request.form.get('amount'))
    # 实现存款逻辑
    return redirect(url_for('bank_info'))

@app.route('/margin_trading', methods=['POST'])
def margin_trading():
    company_id = request.form.get('company_id')
    amount = float(request.form.get('amount'))
    # 实现融资融券逻辑
    return redirect(url_for('exchange_info'))

@app.route('/calculate_interest', methods=['POST'])
def calculate_interest():
    company_id = request.form.get('company_id')
    rate = float(request.form.get('rate'))
    period = int(request.form.get('period'))
    
    # 获取公司对象
    company = Company.query.get_or_404(company_id)
    
    # 计算利息逻辑
    interest = company.capital * rate * period
    return redirect(url_for('bank_info'))

@app.route('/edit_company/<int:company_id>', methods=['POST'])
def edit_company(company_id):
    company = Company.query.get_or_404(company_id)
    company.name = request.form.get('name')
    company.industry = request.form.get('industry')
    company.capital = float(request.form.get('capital'))
    db.session.commit()
    return redirect(url_for('company_detail', company_id=company_id))

@app.route('/distribute_dividend/<int:stock_id>', methods=['POST'])
def distribute_dividend(stock_id):
    amount = float(request.form.get('amount'))
    # 实现分红逻辑
    return redirect(url_for('stock_detail', stock_id=stock_id))

@app.route('/calculate_buyback/<int:company_id>', methods=['POST'])
def calculate_buyback(company_id):
    amount = float(request.form.get('amount'))
    # 实现股票回购逻辑
    return redirect(url_for('company_detail', company_id=company_id))

@app.route('/calculate_bonus_shares/<int:company_id>', methods=['POST'])
def calculate_bonus_shares(company_id):
    ratio = float(request.form.get('ratio'))
    # 实现股票转增股本逻辑
    return redirect(url_for('company_detail', company_id=company_id))

@app.route('/calculate_rights_shares/<int:company_id>', methods=['POST'])
def calculate_rights_shares(company_id):
    ratio = float(request.form.get('ratio'))
    # 实现股票配股逻辑
    return redirect(url_for('company_detail', company_id=company_id))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5010) 