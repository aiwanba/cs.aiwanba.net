from flask import Blueprint, request, jsonify
from models.notification import Notification
from models import db
from datetime import datetime

notification_bp = Blueprint('notification', __name__)

@notification_bp.route('/api/notifications', methods=['GET'])
def get_notifications():
    """获取消息列表"""
    user_id = request.user_id  # 假设通过认证中间件设置
    
    # 获取系统公告和用户相关的消息
    notifications = Notification.query.filter(
        ((Notification.type == 'system') | (Notification.target_id == user_id))
    ).order_by(Notification.created_at.desc()).limit(50).all()
    
    return jsonify([n.to_dict() for n in notifications])

@notification_bp.route('/api/notifications/unread', methods=['GET'])
def get_unread_count():
    """获取未读消息数量"""
    user_id = request.user_id
    
    count = Notification.query.filter(
        ((Notification.type == 'system') | (Notification.target_id == user_id)) &
        (Notification.is_read == False)
    ).count()
    
    return jsonify({'unread_count': count})

@notification_bp.route('/api/notifications/read/<int:notification_id>', methods=['POST'])
def mark_as_read(notification_id):
    """标记消息为已读"""
    notification = Notification.query.get_or_404(notification_id)
    notification.is_read = True
    db.session.commit()
    
    return jsonify({'status': 'success'})

# 消息发送工具函数
def send_notification(type, level, title, content, target_id=None):
    """发送通知"""
    notification = Notification(
        type=type,
        level=level,
        title=title,
        content=content,
        target_id=target_id
    )
    db.session.add(notification)
    db.session.commit() 