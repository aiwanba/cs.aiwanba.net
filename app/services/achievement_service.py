from app import db, websocket_service
from app.models.achievement import (
    Achievement, UserAchievement, AchievementProgress,
    AchievementCategory, AchievementRarity
)
from app.utils.exceptions import AchievementError
from datetime import datetime
import json

class AchievementService:
    def __init__(self):
        self.progress_cache = {}
        self.achievement_cache = {}
        
    def check_achievements(self, user_id, category, action_data):
        """检查是否达成新成就"""
        try:
            # 更新进度
            self._update_progress(user_id, category, action_data)
            
            # 获取用户当前进度
            progress = self._get_user_progress(user_id, category)
            
            # 获取可能达成的成就
            potential_achievements = Achievement.query.filter_by(
                category=category
            ).all()
            
            completed_achievements = []
            
            for achievement in potential_achievements:
                if self._check_conditions(achievement, progress):
                    completed = self._complete_achievement(user_id, achievement.id)
                    if completed:
                        completed_achievements.append(completed)
            
            # 发送通知
            if completed_achievements:
                websocket_service.send_private_notification(
                    user_id,
                    'achievements_unlocked',
                    {
                        'achievements': [
                            {
                                'name': a.achievement.name,
                                'description': a.achievement.description,
                                'points': a.achievement.points,
                                'rarity': a.achievement.rarity
                            }
                            for a in completed_achievements
                        ]
                    }
                )
            
            return completed_achievements
            
        except Exception as e:
            print(f"Achievement check error: {str(e)}")
            return []
    
    def get_user_achievements(self, user_id):
        """获取用户所有成就"""
        return UserAchievement.query.filter_by(
            user_id=user_id
        ).all()
    
    def get_achievement_progress(self, user_id, category=None):
        """获取用户成就进度"""
        query = AchievementProgress.query.filter_by(user_id=user_id)
        if category:
            query = query.filter_by(category=category)
        return query.all()
    
    def _update_progress(self, user_id, category, action_data):
        """更新成就进度"""
        try:
            # 根据不同类别更新不同指标
            if category == AchievementCategory.TRADING.value:
                self._update_trading_progress(user_id, action_data)
            elif category == AchievementCategory.INVESTMENT.value:
                self._update_investment_progress(user_id, action_data)
            elif category == AchievementCategory.SOCIAL.value:
                self._update_social_progress(user_id, action_data)
            elif category == AchievementCategory.COMPANY.value:
                self._update_company_progress(user_id, action_data)
            
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            print(f"Progress update error: {str(e)}")
    
    def _update_trading_progress(self, user_id, action_data):
        """更新交易相关进度"""
        metrics = {
            'total_trades': 1,
            'trade_volume': action_data.get('volume', 0),
            'trade_amount': action_data.get('amount', 0)
        }
        
        for metric, value in metrics.items():
            progress = AchievementProgress.query.filter_by(
                user_id=user_id,
                category=AchievementCategory.TRADING.value,
                metric=metric
            ).first()
            
            if not progress:
                progress = AchievementProgress(
                    user_id=user_id,
                    category=AchievementCategory.TRADING.value,
                    metric=metric
                )
                db.session.add(progress)
            
            progress.value += value
            progress.updated_at = datetime.utcnow()
    
    def _update_investment_progress(self, user_id, action_data):
        """更新投资相关进度"""
        # TODO: 实现投资进度更新
        pass
    
    def _update_social_progress(self, user_id, action_data):
        """更新社交相关进度"""
        # TODO: 实现社交进度更新
        pass
    
    def _update_company_progress(self, user_id, action_data):
        """更新公司相关进度"""
        # TODO: 实现公司进度更新
        pass
    
    def _check_conditions(self, achievement, progress):
        """检查是否满足成就条件"""
        conditions = achievement.conditions
        if not conditions:
            return False
            
        for metric, required_value in conditions.items():
            current_value = next(
                (p.value for p in progress if p.metric == metric),
                0
            )
            if current_value < required_value:
                return False
        
        return True
    
    def _complete_achievement(self, user_id, achievement_id):
        """完成成就"""
        try:
            # 检查是否已获得该成就
            existing = UserAchievement.query.filter_by(
                user_id=user_id,
                achievement_id=achievement_id
            ).first()
            
            if existing and existing.completed:
                return None
            
            if not existing:
                existing = UserAchievement(
                    user_id=user_id,
                    achievement_id=achievement_id
                )
                db.session.add(existing)
            
            existing.completed = True
            existing.completed_at = datetime.utcnow()
            db.session.commit()
            
            return existing
            
        except Exception as e:
            db.session.rollback()
            print(f"Achievement completion error: {str(e)}")
            return None
    
    def _get_user_progress(self, user_id, category):
        """获取用户在指定类别的所有进度"""
        return AchievementProgress.query.filter_by(
            user_id=user_id,
            category=category
        ).all() 