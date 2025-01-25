from app import db, websocket_service
from app.models.market_event import MarketEvent, EventType, EventSeverity
from app.models.company import Company
from app.services.sentiment_service import SentimentService
from datetime import datetime, timedelta
import random

class EventService:
    def __init__(self):
        self.sentiment_service = SentimentService()
        self.event_thresholds = {
            'price_change': 0.1,      # 10%价格变化
            'volume_change': 0.3,     # 30%交易量变化
            'volatility': 0.15,       # 15%波动率
            'sentiment_change': 0.2   # 20%情绪变化
        }
    
    def check_for_events(self):
        """检查并生成市场事件"""
        self._check_price_events()
        self._check_volume_events()
        self._check_volatility_events()
        self._check_ai_behavior_events()
        self._cleanup_expired_events()
    
    def _check_price_events(self):
        """检查价格相关事件"""
        companies = Company.query.all()
        for company in companies:
            # 获取24小时价格变化
            price_change = self._calculate_price_change(company.id)
            
            if abs(price_change) >= self.event_thresholds['price_change']:
                event_type = EventType.PRICE_SURGE.value if price_change > 0 else EventType.PRICE_CRASH.value
                severity = self._determine_severity(abs(price_change))
                
                self.create_event(
                    type=event_type,
                    severity=severity,
                    company_id=company.id,
                    title=f"{'价格暴涨' if price_change > 0 else '价格暴跌'}: {company.name}",
                    description=f"公司股价在24小时内{'上涨' if price_change > 0 else '下跌'}{abs(price_change)*100:.1f}%",
                    impact_score=price_change
                )
    
    def _check_volume_events(self):
        """检查交易量相关事件"""
        companies = Company.query.all()
        for company in companies:
            volume_change = self._calculate_volume_change(company.id)
            
            if volume_change >= self.event_thresholds['volume_change']:
                self.create_event(
                    type=EventType.VOLUME_SPIKE.value,
                    severity=self._determine_severity(volume_change),
                    company_id=company.id,
                    title=f"交易量激增: {company.name}",
                    description=f"公司交易量在24小时内增加{volume_change*100:.1f}%",
                    impact_score=min(volume_change/2, 1.0)
                )
    
    def _check_volatility_events(self):
        """检查波动率相关事件"""
        companies = Company.query.all()
        for company in companies:
            volatility = self._calculate_volatility(company.id)
            
            if volatility >= self.event_thresholds['volatility']:
                self.create_event(
                    type=EventType.HIGH_VOLATILITY.value,
                    severity=self._determine_severity(volatility),
                    company_id=company.id,
                    title=f"高波动性警告: {company.name}",
                    description=f"公司股价波动率达到{volatility*100:.1f}%",
                    impact_score=-volatility  # 高波动通常被视为负面
                )
    
    def _check_ai_behavior_events(self):
        """检查AI行为相关事件"""
        companies = Company.query.all()
        for company in companies:
            ai_sentiment = self.sentiment_service._analyze_ai_behavior(company.id)
            
            if abs(ai_sentiment) >= 0.7:  # AI行为强烈偏向某一方向
                self.create_event(
                    type=EventType.AI_BEHAVIOR.value,
                    severity=EventSeverity.MEDIUM.value,
                    company_id=company.id,
                    title=f"AI交易者{'看多' if ai_sentiment > 0 else '看空'}: {company.name}",
                    description=f"AI交易者表现出强烈的{'买入' if ai_sentiment > 0 else '卖出'}倾向",
                    impact_score=ai_sentiment
                )
    
    def create_event(self, type, severity, title, description, impact_score, company_id=None):
        """创建新的市场事件"""
        try:
            # 检查是否已存在类似事件
            existing_event = MarketEvent.query.filter_by(
                type=type,
                company_id=company_id,
                is_active=True
            ).first()
            
            if existing_event:
                # 更新现有事件
                existing_event.severity = severity
                existing_event.impact_score = impact_score
                existing_event.expires_at = datetime.utcnow() + timedelta(hours=4)
                db.session.commit()
            else:
                # 创建新事件
                event = MarketEvent(
                    type=type,
                    severity=severity,
                    company_id=company_id,
                    title=title,
                    description=description,
                    impact_score=impact_score,
                    expires_at=datetime.utcnow() + timedelta(hours=4)
                )
                db.session.add(event)
                db.session.commit()
                
                # 通过WebSocket广播事件
                websocket_service.broadcast_market_event(event.type, event.to_dict())
                
        except Exception as e:
            db.session.rollback()
            print(f"Event creation error: {str(e)}")
    
    def _cleanup_expired_events(self):
        """清理过期事件"""
        expired_events = MarketEvent.query.filter(
            MarketEvent.expires_at <= datetime.utcnow(),
            MarketEvent.is_active == True
        ).all()
        
        for event in expired_events:
            event.is_active = False
        
        db.session.commit()
    
    def _determine_severity(self, value):
        """根据数值确定事件严重程度"""
        if value >= 0.3:
            return EventSeverity.CRITICAL.value
        elif value >= 0.2:
            return EventSeverity.HIGH.value
        elif value >= 0.1:
            return EventSeverity.MEDIUM.value
        else:
            return EventSeverity.LOW.value
    
    # ... 其他辅助方法（_calculate_price_change, _calculate_volume_change等）... 