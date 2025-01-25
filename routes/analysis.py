from flask import Blueprint, render_template, jsonify, request
from services.analysis import AnalysisService
from models import MarketAnalysis, CompanyAnalysis, TechnicalIndicator

analysis_bp = Blueprint('analysis', __name__)

@analysis_bp.route('/')
def analysis_page():
    """市场分析主页"""
    return render_template('analysis/index.html')

@analysis_bp.route('/market')
def market_analysis():
    """获取市场分析数据"""
    # 获取最近30天的市场数据
    market_data = MarketAnalysis.query\
        .order_by(MarketAnalysis.date.desc())\
        .limit(30).all()
    
    data = [{
        'date': item.date.strftime('%Y-%m-%d'),
        'market_value': float(item.market_value),
        'trading_volume': item.trading_volume,
        'active_companies': item.active_companies,
        'price_index': float(item.price_index)
    } for item in market_data]
    
    return jsonify({
        'success': True,
        'data': data
    })

@analysis_bp.route('/company/<int:company_id>')
def company_analysis(company_id):
    """获取公司分析数据"""
    # 获取最近30天的公司数据
    company_data = CompanyAnalysis.query\
        .filter_by(company_id=company_id)\
        .order_by(CompanyAnalysis.date.desc())\
        .limit(30).all()
    
    data = [{
        'date': item.date.strftime('%Y-%m-%d'),
        'open': float(item.open_price),
        'close': float(item.close_price),
        'high': float(item.high_price),
        'low': float(item.low_price),
        'volume': item.volume,
        'turnover': float(item.turnover),
        'pe_ratio': float(item.pe_ratio) if item.pe_ratio else None,
        'pb_ratio': float(item.pb_ratio) if item.pb_ratio else None
    } for item in company_data]
    
    return jsonify({
        'success': True,
        'data': data
    })

@analysis_bp.route('/technical/<int:company_id>')
def technical_analysis(company_id):
    """获取技术指标数据"""
    # 获取最近30天的技术指标
    indicators = TechnicalIndicator.query\
        .filter_by(company_id=company_id)\
        .order_by(TechnicalIndicator.date.desc())\
        .limit(30).all()
    
    data = [{
        'date': item.date.strftime('%Y-%m-%d'),
        'ma5': float(item.ma5) if item.ma5 else None,
        'ma10': float(item.ma10) if item.ma10 else None,
        'ma20': float(item.ma20) if item.ma20 else None,
        'rsi': float(item.rsi) if item.rsi else None,
        'kdj_k': float(item.kdj_k) if item.kdj_k else None,
        'kdj_d': float(item.kdj_d) if item.kdj_d else None,
        'kdj_j': float(item.kdj_j) if item.kdj_j else None,
        'macd': float(item.macd) if item.macd else None
    } for item in indicators]
    
    return jsonify({
        'success': True,
        'data': data
    })

@analysis_bp.route('/calculate/market', methods=['POST'])
def calculate_market():
    """计算市场分析数据"""
    success, result = AnalysisService.calculate_market_analysis()
    if success:
        return jsonify({
            'success': True,
            'message': '计算完成'
        })
    return jsonify({
        'success': False,
        'message': result
    })

@analysis_bp.route('/calculate/technical/<int:company_id>', methods=['POST'])
def calculate_technical(company_id):
    """计算技术指标"""
    success, result = AnalysisService.calculate_technical_indicators(company_id)
    if success:
        return jsonify({
            'success': True,
            'message': '计算完成'
        })
    return jsonify({
        'success': False,
        'message': result
    }) 