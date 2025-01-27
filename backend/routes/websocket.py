from flask_socketio import emit, join_room, leave_room
from app import socketio
from flask import request
from models import User

@socketio.on('connect', namespace='/market')
def handle_market_connect():
    """处理市场频道连接"""
    emit('connect_response', {'status': 'connected'})

@socketio.on('subscribe_company', namespace='/market')
def handle_company_subscribe(data):
    """订阅公司行情"""
    company_id = data.get('company_id')
    if company_id:
        room = f'company_{company_id}'
        join_room(room)
        emit('subscribe_response', {
            'status': 'subscribed',
            'company_id': company_id
        })

@socketio.on('connect', namespace='/bank')
def handle_bank_connect():
    """处理银行频道连接"""
    emit('connect_response', {'status': 'connected'})

@socketio.on('subscribe_bank', namespace='/bank')
def handle_bank_subscribe(data):
    """订阅银行信息"""
    bank_id = data.get('bank_id')
    if bank_id:
        room = f'bank_{bank_id}'
        join_room(room)
        emit('subscribe_response', {
            'status': 'subscribed',
            'bank_id': bank_id
        }) 