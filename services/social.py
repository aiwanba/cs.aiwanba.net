from models import db, Team, TeamMember, TeamDiscussion, DiscussionComment, UserMessage, User
from datetime import datetime

class SocialService:
    """社交服务"""
    
    @staticmethod
    def create_team(name, description, leader_id):
        """创建团队"""
        if Team.query.filter_by(name=name).first():
            return False, "团队名称已存在"
            
        team = Team(name=name, description=description, leader_id=leader_id)
        member = TeamMember(user_id=leader_id, role='leader')
        team.members.append(member)
        
        try:
            db.session.add(team)
            db.session.commit()
            return True, team
        except Exception as e:
            db.session.rollback()
            return False, str(e)
    
    @staticmethod
    def join_team(team_id, user_id):
        """加入团队"""
        if TeamMember.query.filter_by(team_id=team_id, user_id=user_id).first():
            return False, "已经是团队成员"
            
        member = TeamMember(team_id=team_id, user_id=user_id)
        try:
            db.session.add(member)
            db.session.commit()
            return True, member
        except Exception as e:
            db.session.rollback()
            return False, str(e)
    
    @staticmethod
    def create_discussion(team_id, user_id, title, content):
        """创建讨论"""
        if not TeamMember.query.filter_by(team_id=team_id, user_id=user_id).first():
            return False, "不是团队成员"
            
        discussion = TeamDiscussion(
            team_id=team_id,
            user_id=user_id,
            title=title,
            content=content
        )
        
        try:
            db.session.add(discussion)
            db.session.commit()
            return True, discussion
        except Exception as e:
            db.session.rollback()
            return False, str(e)
    
    @staticmethod
    def add_comment(discussion_id, user_id, content):
        """添加评论"""
        discussion = TeamDiscussion.query.get(discussion_id)
        if not discussion:
            return False, "讨论不存在"
            
        if not TeamMember.query.filter_by(
            team_id=discussion.team_id, 
            user_id=user_id
        ).first():
            return False, "不是团队成员"
            
        comment = DiscussionComment(
            discussion_id=discussion_id,
            user_id=user_id,
            content=content
        )
        
        try:
            db.session.add(comment)
            db.session.commit()
            return True, comment
        except Exception as e:
            db.session.rollback()
            return False, str(e)
    
    @staticmethod
    def send_message(sender_id, receiver_id, content):
        """发送私信"""
        message = UserMessage(
            sender_id=sender_id,
            receiver_id=receiver_id,
            content=content
        )
        
        try:
            db.session.add(message)
            db.session.commit()
            return True, message
        except Exception as e:
            db.session.rollback()
            return False, str(e)
    
    @staticmethod
    def get_unread_messages(user_id):
        """获取未读消息"""
        return UserMessage.query.filter_by(
            receiver_id=user_id,
            read=False
        ).order_by(UserMessage.created_at.desc()).all()
    
    @staticmethod
    def mark_message_read(message_id):
        """标记消息已读"""
        message = UserMessage.query.get(message_id)
        if message:
            message.read = True
            db.session.commit()
            return True
        return False 