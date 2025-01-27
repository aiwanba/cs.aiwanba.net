from flask_socketio import emit
from app import socketio
from decimal import Decimal
import json

class WebSocketService:
    @staticmethod
    def broadcast_stock_price(company_id, new_price):
        """广播股票价格变动"""
        data = {
            'company_id': company_id,
            'price': float(new_price)
        }
        socketio.emit('stock_price_update', data, namespace='/market')
        
    @staticmethod
    def broadcast_transaction(transaction_data):
        """广播交易信息"""
        socketio.emit('new_transaction', transaction_data, namespace='/market')
        
    @staticmethod
    def broadcast_bank_update(bank_id, update_type, data):
        """广播银行信息更新"""
        message = {
            'bank_id': bank_id,
            'type': update_type,
            'data': data
        }
        socketio.emit('bank_update', message, namespace='/bank') 