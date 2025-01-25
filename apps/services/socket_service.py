from datetime import datetime
from apps.extensions import socketio, db
from apps.models.company import Company
from apps.models.transaction import Transaction

class SocketService:
    @staticmethod
    def emit_market_update():
        """推送市场数据更新"""
        companies = Company.query.all()
        market_data = []
        total_market_value = 0
        
        for company in companies:
            market_value = company.market_value()
            total_market_value += market_value
            
            market_data.append({
                'id': company.id,
                'name': company.name,
                'current_price': float(company.current_price),
                'available_shares': company.available_shares,
                'market_value': market_value
            })
        
        socketio.emit('market_update', {
            'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
            'companies': market_data,
            'total_market_value': total_market_value
        })
    
    @staticmethod
    def emit_transaction(transaction):
        """推送交易信息"""
        socketio.emit('transaction', {
            'id': transaction.id,
            'type': transaction.type,
            'company_name': transaction.company.name,
            'shares': transaction.shares,
            'price': float(transaction.price),
            'total_amount': float(transaction.total_amount),
            'timestamp': transaction.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }, room=str(transaction.company_id))
    
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