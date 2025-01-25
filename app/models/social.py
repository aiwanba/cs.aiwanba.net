from app import db
from datetime import datetime
from enum import Enum

class ChatRoomType(Enum):
    PUBLIC = 'public'      # 公共聊天室
    PRIVATE = 'private'    # 私人聊天室
    ALLIANCE = 'alliance'  # 联盟聊天室

class MessageType(Enum):
    TEXT = 'text'         # 文本消息
    TRADE = 'trade'       # 交易消息
    SYSTEM = 'system'     # 系统消息
    IMAGE = 'image'       # 图片消息

class Alliance(db.Model):
    __tablename__ = 'alliances'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    founder_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    min_assets = db.Column(db.Float, default=0.0)  # 加入门槛
    member_count = db.Column(db.Integer, default=1)
    total_assets = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    members = db.relationship('AllianceMember', backref='alliance', lazy=True)
    chat_room = db.relationship('ChatRoom', backref='alliance', uselist=False)

class AllianceMember(db.Model):
    __tablename__ = 'alliance_members'
    
    id = db.Column(db.Integer, primary_key=True)
    alliance_id = db.Column(db.Integer, db.ForeignKey('alliances.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role = db.Column(db.String(20), default='member')  # founder, admin, member
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 联合唯一索引确保用户只能加入一个联盟
    __table_args__ = (db.UniqueConstraint('user_id', name='unique_alliance_member'),)

class ChatRoom(db.Model):
    __tablename__ = 'chat_rooms'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(20), nullable=False)
    alliance_id = db.Column(db.Integer, db.ForeignKey('alliances.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    messages = db.relationship('ChatMessage', backref='chat_room', lazy=True)
    participants = db.relationship('ChatParticipant', backref='chat_room', lazy=True)
    
    def __init__(self, name, type):
        if type not in [t.value for t in ChatRoomType]:
            raise ValueError("Invalid chat room type")
        self.name = name
        self.type = type

class ChatParticipant(db.Model):
    __tablename__ = 'chat_participants'
    
    id = db.Column(db.Integer, primary_key=True)
    chat_room_id = db.Column(db.Integer, db.ForeignKey('chat_rooms.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    last_read_at = db.Column(db.DateTime, default=datetime.utcnow)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 联合唯一索引确保用户在一个聊天室中只有一个参与记录
    __table_args__ = (db.UniqueConstraint('chat_room_id', 'user_id', name='unique_chat_participant'),)

class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    chat_room_id = db.Column(db.Integer, db.ForeignKey('chat_rooms.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # 系统消息可能没有发送者
    type = db.Column(db.String(20), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, chat_room_id, content, type='text', sender_id=None):
        if type not in [t.value for t in MessageType]:
            raise ValueError("Invalid message type")
        self.chat_room_id = chat_room_id
        self.sender_id = sender_id
        self.type = type
        self.content = content
    
    def to_dict(self):
        return {
            'id': self.id,
            'chat_room_id': self.chat_room_id,
            'sender_id': self.sender_id,
            'type': self.type,
            'content': self.content,
            'created_at': self.created_at.isoformat()
        }

class ForumCategory(db.Model):
    __tablename__ = 'forum_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    topics = db.relationship('ForumTopic', backref='category', lazy=True)

class ForumTopic(db.Model):
    __tablename__ = 'forum_topics'
    
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('forum_categories.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    views = db.Column(db.Integer, default=0)
    replies = db.Column(db.Integer, default=0)
    is_pinned = db.Column(db.Boolean, default=False)
    is_locked = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    posts = db.relationship('ForumPost', backref='topic', lazy=True)

class ForumPost(db.Model):
    __tablename__ = 'forum_posts'
    
    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('forum_topics.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    likes = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow) 