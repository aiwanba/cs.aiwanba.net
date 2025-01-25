from flask_socketio import emit
from app import socketio, db
from apps.models.company import Company
from apps.models.transaction import Transaction
from datetime import datetime

class SocketService:
    @staticmethod
    def emit_market_update():
        """推送市场数据更新"""
        companies = Company.query.all()
        market_data = [{
            'id': company.id,
            'name': company.name,
            'current_price': float(company.current_price),
            'available_shares': company.available_shares,
            'total_shares': company.total_shares,
            'market_value': company.market_value()
        } for company in companies]
        
        socketio.emit('market_update', {
            'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
            'data': market_data
        })
    
    @staticmethod
    def emit_transaction_update(transaction):
        """推送交易更新"""
        socketio.emit('transaction_update', {
            'id': transaction.id,
            'type': transaction.type,
            'company_name': transaction.company.name,
            'shares': transaction.shares,
            'price': float(transaction.price),
            'total_amount': float(transaction.total_amount),
            'created_at': transaction.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    @staticmethod
    def emit_news_update(news):
        """推送新闻更新"""
        socketio.emit('news_update', {
            'id': news.id,
            'title': news.title,
            'content': news.content,
            'type': news.type,
            'company_name': news.company.name if news.company else None,
            'impact': news.impact,
            'created_at': news.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }) 