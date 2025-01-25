from flask_socketio import emit, join_room, leave_room
from functools import wraps
from app import socketio
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
import json
import redis
from datetime import datetime

class WebSocketService:
    def __init__(self):
        self.redis_client = redis.from_url('redis://localhost:6379/0')
        self.connected_users = set()
        
    def authenticate_socket(self, f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            try:
                verify_jwt_in_request()
                return f(*args, **kwargs)
            except Exception as e:
                return False
        return wrapped
    
    def handle_connect(self):
        """处理客户端连接"""
        try:
            verify_jwt_in_request()
            user_id = str(get_jwt_identity())
            join_room(user_id)
            self.connected_users.add(user_id)
            
            # 发送当前市场状态
            market_data = self._get_market_data()
            emit('market_state', market_data, room=user_id)
            
            # 广播用户在线状态
            emit('user_connected', {
                'user_id': user_id,
                'online_users': len(self.connected_users)
            }, broadcast=True)
            
        except Exception as e:
            emit('error', {'message': 'Authentication failed'})
    
    def handle_disconnect(self):
        """处理客户端断开连接"""
        try:
            verify_jwt_in_request()
            user_id = str(get_jwt_identity())
            leave_room(user_id)
            self.connected_users.discard(user_id)
            
            # 广播用户离线状态
            emit('user_disconnected', {
                'user_id': user_id,
                'online_users': len(self.connected_users)
            }, broadcast=True)
            
        except Exception:
            pass
    
    def broadcast_stock_update(self, company_id, price, volume, price_change=None, price_change_percent=None, market_cap=None):
        """广播股票价格更新"""
        data = {
            'company_id': company_id,
            'price': price,
            'volume': volume,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if price_change is not None:
            data['price_change'] = price_change
        if price_change_percent is not None:
            data['price_change_percent'] = price_change_percent
        if market_cap is not None:
            data['market_cap'] = market_cap
        
        emit('stock_update', data, broadcast=True)
        self._update_market_data(data)
    
    def broadcast_transaction(self, transaction_data):
        """广播交易信息"""
        emit('transaction', transaction_data, broadcast=True)
        self._update_market_data(transaction_data)
    
    def broadcast_market_event(self, event_type, event_data):
        """广播市场事件"""
        data = {
            'type': event_type,
            'data': event_data,
            'timestamp': datetime.utcnow().isoformat()
        }
        emit('market_event', data, broadcast=True)
    
    def send_private_notification(self, user_id, notification_type, notification_data):
        """发送私人通知"""
        data = {
            'type': notification_type,
            'data': notification_data,
            'timestamp': datetime.utcnow().isoformat()
        }
        emit('private_notification', data, room=str(user_id))
    
    def _get_market_data(self):
        """获取市场数据"""
        data = self.redis_client.get('market_data')
        return json.loads(data) if data else {}
    
    def _update_market_data(self, new_data):
        """更新市场数据"""
        market_data = self._get_market_data()
        
        # 更新相关数据
        if 'price' in new_data:
            market_data.setdefault('price_history', []).append({
                'price': new_data['price'],
                'timestamp': new_data['timestamp']
            })
            # 只保留最近100条价格记录
            market_data['price_history'] = market_data['price_history'][-100:]
        
        if 'volume' in new_data:
            market_data['total_volume'] = market_data.get('total_volume', 0) + new_data['volume']
        
        # 缓存更新后的数据（30秒过期）
        self.redis_client.setex('market_data', 30, json.dumps(market_data)) 