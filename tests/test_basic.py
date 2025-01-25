def test_index(client):
    """测试首页访问"""
    response = client.get('/')
    assert response.status_code == 200

def test_market_data(client):
    """测试市场数据API"""
    response = client.get('/api/market/data')
    assert response.status_code == 200
    assert 'companies' in response.json

def test_websocket(client):
    """测试WebSocket连接"""
    from flask_socketio import SocketIOTestClient
    from app import socketio
    
    socket_client = SocketIOTestClient(app, socketio)
    socket_client.connect()
    assert socket_client.is_connected() 