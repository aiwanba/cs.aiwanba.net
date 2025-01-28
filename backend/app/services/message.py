from datetime import datetime, timedelta
from app import db
from app.models.message import Message, MessageRecipient
from app.models.user import User

class MessageService:
    @staticmethod
    def create_message(type, title, content, related_id=None, priority=3, expire_days=1, user_ids=None):
        """创建消息"""
        try:
            # 创建消息
            message = Message(
                type=type,
                title=title,
                content=content,
                related_id=related_id,
                priority=priority,
                expire_days=expire_days
            )
            db.session.add(message)
            db.session.flush()  # 获取消息ID
            
            # 如果指定了接收者，创建接收记录
            if user_ids:
                recipients = []
                for user_id in user_ids:
                    recipient = MessageRecipient(
                        message_id=message.id,
                        user_id=user_id
                    )
                    recipients.append(recipient)
                db.session.bulk_save_objects(recipients)
            
            db.session.commit()
            return True, message
        except Exception as e:
            db.session.rollback()
            return False, str(e)
    
    @staticmethod
    def broadcast_message(type, title, content, related_id=None, priority=3, expire_days=1):
        """广播消息给所有用户"""
        try:
            # 创建消息
            message = Message(
                type=type,
                title=title,
                content=content,
                related_id=related_id,
                priority=priority,
                expire_days=expire_days
            )
            db.session.add(message)
            db.session.flush()
            
            # 获取所有活跃用户
            users = User.query.filter_by(status=1).all()
            
            # 创建接收记录
            recipients = []
            for user in users:
                recipient = MessageRecipient(
                    message_id=message.id,
                    user_id=user.id
                )
                recipients.append(recipient)
            
            db.session.bulk_save_objects(recipients)
            db.session.commit()
            return True, message
        except Exception as e:
            db.session.rollback()
            return False, str(e)
    
    @staticmethod
    def get_user_messages(user_id, type=None, is_read=None, page=1, per_page=10):
        """获取用户消息列表"""
        query = MessageRecipient.query.filter_by(user_id=user_id)
        
        if is_read is not None:
            query = query.filter_by(is_read=is_read)
        
        if type:
            query = query.join(Message).filter(Message.type == type)
        
        recipients = query.order_by(MessageRecipient.created_at.desc())\
                        .paginate(page=page, per_page=per_page, error_out=False)
        
        return {
            'items': [recipient.to_dict() for recipient in recipients.items],
            'total': recipients.total,
            'pages': recipients.pages,
            'current_page': recipients.page
        }
    
    @staticmethod
    def mark_as_read(message_id, user_id):
        """标记消息为已读"""
        recipient = MessageRecipient.query.filter_by(
            message_id=message_id,
            user_id=user_id
        ).first()
        
        if not recipient:
            return False, "消息不存在"
        
        try:
            recipient.mark_read()
            return True, recipient
        except Exception as e:
            db.session.rollback()
            return False, str(e)
    
    @staticmethod
    def get_unread_count(user_id):
        """获取未读消息数量"""
        return MessageRecipient.query.filter_by(
            user_id=user_id,
            is_read=0
        ).count()
    
    @staticmethod
    def clean_expired_messages():
        """清理过期消息"""
        try:
            expired_messages = Message.query.filter(
                Message.expire_at <= datetime.utcnow(),
                Message.status == 1
            ).all()
            
            for message in expired_messages:
                message.mark_expired()
            
            db.session.commit()
            return True, len(expired_messages)
        except Exception as e:
            db.session.rollback()
            return False, str(e) 