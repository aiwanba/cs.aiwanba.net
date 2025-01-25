from app import db, websocket_service
from app.models.social import (
    Alliance, AllianceMember, ChatRoom, ChatParticipant, 
    ChatMessage, ForumCategory, ForumTopic, ForumPost,
    ChatRoomType, MessageType
)
from app.utils.exceptions import SocialError
from datetime import datetime
import json

class SocialService:
    def __init__(self):
        self.max_alliance_members = 100  # 联盟最大成员数
        self.max_chat_history = 100     # 最大聊天历史记录数
    
    def create_alliance(self, name, description, founder_id, min_assets=0):
        """创建投资联盟"""
        try:
            # 检查用户是否已在其他联盟
            existing = AllianceMember.query.filter_by(user_id=founder_id).first()
            if existing:
                raise SocialError("Already in an alliance")
            
            alliance = Alliance(
                name=name,
                description=description,
                founder_id=founder_id,
                min_assets=min_assets
            )
            
            # 创建联盟聊天室
            chat_room = ChatRoom(
                name=f"Alliance: {name}",
                type=ChatRoomType.ALLIANCE.value
            )
            
            # 创建创始人成员记录
            member = AllianceMember(
                alliance_id=alliance.id,
                user_id=founder_id,
                role='founder'
            )
            
            db.session.add(alliance)
            db.session.add(chat_room)
            db.session.add(member)
            db.session.commit()
            
            # 创建系统消息
            self.send_chat_message(
                chat_room.id,
                None,
                f"Alliance {name} has been created!",
                MessageType.SYSTEM.value
            )
            
            return alliance
            
        except Exception as e:
            db.session.rollback()
            raise SocialError(str(e))
    
    def join_alliance(self, alliance_id, user_id):
        """加入联盟"""
        try:
            alliance = Alliance.query.get(alliance_id)
            if not alliance:
                raise SocialError("Alliance not found")
            
            # 检查是否已在其他联盟
            existing = AllianceMember.query.filter_by(user_id=user_id).first()
            if existing:
                raise SocialError("Already in an alliance")
            
            # 检查成员数限制
            if alliance.member_count >= self.max_alliance_members:
                raise SocialError("Alliance is full")
            
            # 检查资产门槛
            if not self._check_user_assets(user_id, alliance.min_assets):
                raise SocialError("Insufficient assets")
            
            member = AllianceMember(
                alliance_id=alliance_id,
                user_id=user_id
            )
            
            alliance.member_count += 1
            
            db.session.add(member)
            db.session.commit()
            
            # 加入联盟聊天室
            self.join_chat_room(alliance.chat_room.id, user_id)
            
            # 发送系统消息
            self.send_chat_message(
                alliance.chat_room.id,
                None,
                f"User {user_id} has joined the alliance!",
                MessageType.SYSTEM.value
            )
            
            return member
            
        except Exception as e:
            db.session.rollback()
            raise SocialError(str(e))
    
    def create_chat_room(self, name, type, creator_id, alliance_id=None):
        """创建聊天室"""
        try:
            chat_room = ChatRoom(name=name, type=type)
            if alliance_id:
                chat_room.alliance_id = alliance_id
            
            # 创建者自动加入
            participant = ChatParticipant(
                chat_room_id=chat_room.id,
                user_id=creator_id
            )
            
            db.session.add(chat_room)
            db.session.add(participant)
            db.session.commit()
            
            return chat_room
            
        except Exception as e:
            db.session.rollback()
            raise SocialError(str(e))
    
    def join_chat_room(self, chat_room_id, user_id):
        """加入聊天室"""
        try:
            chat_room = ChatRoom.query.get(chat_room_id)
            if not chat_room:
                raise SocialError("Chat room not found")
            
            # 检查权限
            if chat_room.type == ChatRoomType.ALLIANCE.value:
                if not self._check_alliance_membership(chat_room.alliance_id, user_id):
                    raise SocialError("Not a member of this alliance")
            
            participant = ChatParticipant(
                chat_room_id=chat_room_id,
                user_id=user_id
            )
            
            db.session.add(participant)
            db.session.commit()
            
            # 加入WebSocket房间
            websocket_service.join_chat_room(chat_room_id, user_id)
            
            return participant
            
        except Exception as e:
            db.session.rollback()
            raise SocialError(str(e))
    
    def send_chat_message(self, chat_room_id, sender_id, content, type=MessageType.TEXT.value):
        """发送聊天消息"""
        try:
            chat_room = ChatRoom.query.get(chat_room_id)
            if not chat_room:
                raise SocialError("Chat room not found")
            
            # 检查发送权限
            if sender_id and not self._check_chat_permission(chat_room_id, sender_id):
                raise SocialError("Not authorized to send message")
            
            message = ChatMessage(
                chat_room_id=chat_room_id,
                sender_id=sender_id,
                content=content,
                type=type
            )
            
            db.session.add(message)
            db.session.commit()
            
            # 通过WebSocket广播消息
            websocket_service.broadcast_chat_message(message.to_dict())
            
            return message
            
        except Exception as e:
            db.session.rollback()
            raise SocialError(str(e))
    
    def create_forum_topic(self, category_id, author_id, title, content):
        """创建论坛主题"""
        try:
            topic = ForumTopic(
                category_id=category_id,
                author_id=author_id,
                title=title,
                content=content
            )
            
            db.session.add(topic)
            db.session.commit()
            
            return topic
            
        except Exception as e:
            db.session.rollback()
            raise SocialError(str(e))
    
    def reply_forum_topic(self, topic_id, author_id, content):
        """回复论坛主题"""
        try:
            topic = ForumTopic.query.get(topic_id)
            if not topic:
                raise SocialError("Topic not found")
            
            if topic.is_locked:
                raise SocialError("Topic is locked")
            
            post = ForumPost(
                topic_id=topic_id,
                author_id=author_id,
                content=content
            )
            
            topic.replies += 1
            topic.updated_at = datetime.utcnow()
            
            db.session.add(post)
            db.session.commit()
            
            return post
            
        except Exception as e:
            db.session.rollback()
            raise SocialError(str(e))
    
    def _check_user_assets(self, user_id, min_assets):
        """检查用户资产是否达到要求"""
        # TODO: 实现资产检查
        return True
    
    def _check_alliance_membership(self, alliance_id, user_id):
        """检查用户是否是联盟成员"""
        return AllianceMember.query.filter_by(
            alliance_id=alliance_id,
            user_id=user_id
        ).first() is not None
    
    def _check_chat_permission(self, chat_room_id, user_id):
        """检查用户是否有权限在聊天室发言"""
        return ChatParticipant.query.filter_by(
            chat_room_id=chat_room_id,
            user_id=user_id
        ).first() is not None 