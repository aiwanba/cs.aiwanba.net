from app import db, websocket_service
from app.models.news import News, NewsTemplate, NewsType, NewsSource, NewsImpact
from app.models.company import Company
from app.models.market_event import MarketEvent
from app.services.sentiment_service import SentimentService
from datetime import datetime, timedelta
import random
import json

class NewsService:
    def __init__(self):
        self.sentiment_service = SentimentService()
        self.news_cache = {}
        self.template_cache = {}
        
    def generate_market_news(self):
        """生成市场新闻"""
        try:
            # 获取市场情绪
            market_sentiment = self.sentiment_service.analyze_market_sentiment()
            
            # 获取活跃公司
            active_companies = self._get_active_companies()
            
            # 获取市场事件
            market_events = self._get_recent_market_events()
            
            # 根据市场状态生成新闻
            news_items = []
            
            # 基于市场情绪生成新闻
            if abs(market_sentiment) >= 0.5:
                news_items.append(
                    self._generate_sentiment_news(market_sentiment)
                )
            
            # 基于活跃公司生成新闻
            for company in active_companies:
                if random.random() < 0.3:  # 30%概率生成公司新闻
                    news_items.append(
                        self._generate_company_news(company)
                    )
            
            # 基于市场事件生成新闻
            for event in market_events:
                news_items.append(
                    self._generate_event_news(event)
                )
            
            # 保存并广播新闻
            for news in news_items:
                if news:
                    db.session.add(news)
                    websocket_service.broadcast_news(news.to_dict())
            
            db.session.commit()
            
            return news_items
            
        except Exception as e:
            db.session.rollback()
            print(f"News generation error: {str(e)}")
            return []
    
    def generate_player_news(self, user_id, action_type, action_data):
        """根据玩家行为生成新闻"""
        try:
            template = self._get_player_news_template(action_type)
            if not template:
                return None
            
            # 填充模板
            title = template.title_template.format(**action_data)
            content = template.content_template.format(**action_data)
            
            # 计算影响
            impact = self._calculate_news_impact(
                action_type,
                action_data,
                template.impact_factors
            )
            
            news = News(
                type=NewsType.SOCIAL.value,
                source=NewsSource.PLAYER.value,
                title=title,
                content=content,
                impact=impact,
                trigger_user_id=user_id,
                expires_at=datetime.utcnow() + timedelta(hours=24)
            )
            
            db.session.add(news)
            db.session.commit()
            
            # 广播新闻
            websocket_service.broadcast_news(news.to_dict())
            
            return news
            
        except Exception as e:
            db.session.rollback()
            print(f"Player news generation error: {str(e)}")
            return None
    
    def _get_active_companies(self):
        """获取活跃公司"""
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        return Company.query.filter(
            Company.last_trade_time >= cutoff_time
        ).all()
    
    def _get_recent_market_events(self):
        """获取近期市场事件"""
        cutoff_time = datetime.utcnow() - timedelta(hours=6)
        return MarketEvent.query.filter(
            MarketEvent.created_at >= cutoff_time,
            MarketEvent.is_active == True
        ).all()
    
    def _generate_sentiment_news(self, sentiment):
        """生成市场情绪新闻"""
        template = self._get_sentiment_news_template(sentiment)
        if not template:
            return None
            
        return News(
            type=NewsType.MARKET.value,
            source=NewsSource.SYSTEM.value,
            title=template['title'],
            content=template['content'],
            impact=int(sentiment * 2),  # 转换为-2到2的范围
            expires_at=datetime.utcnow() + timedelta(hours=12)
        )
    
    def _generate_company_news(self, company):
        """生成公司新闻"""
        # 获取公司表现数据
        performance = self._analyze_company_performance(company)
        
        template = self._get_company_news_template(performance)
        if not template:
            return None
            
        return News(
            type=NewsType.COMPANY.value,
            source=NewsSource.AI.value,
            title=template['title'].format(company_name=company.name),
            content=template['content'].format(
                company_name=company.name,
                **performance
            ),
            impact=performance['sentiment'],
            company_id=company.id,
            expires_at=datetime.utcnow() + timedelta(hours=24)
        )
    
    def _generate_event_news(self, event):
        """根据市场事件生成新闻"""
        template = self._get_event_news_template(event.type)
        if not template:
            return None
            
        return News(
            type=NewsType.MARKET.value,
            source=NewsSource.MARKET.value,
            title=template['title'].format(event=event),
            content=template['content'].format(event=event),
            impact=event.impact_score,
            company_id=event.company_id,
            expires_at=event.expires_at
        )
    
    def _analyze_company_performance(self, company):
        """分析公司表现"""
        # TODO: 实现更复杂的公司分析
        return {
            'price_change': random.uniform(-0.1, 0.1),
            'volume_change': random.uniform(-0.2, 0.2),
            'sentiment': random.randint(-2, 2)
        }
    
    def _get_sentiment_news_template(self, sentiment):
        """获取情绪新闻模板"""
        templates = {
            'very_positive': {
                'title': '市场情绪高涨，投资者信心十足',
                'content': '市场呈现出强劲的上涨势头，投资者信心指数创下新高...'
            },
            'positive': {
                'title': '市场维持乐观，交投活跃',
                'content': '市场保持积极态势，成交量稳步提升...'
            },
            'negative': {
                'title': '市场情绪谨慎，观望情绪浓厚',
                'content': '市场出现回调，投资者保持谨慎态度...'
            },
            'very_negative': {
                'title': '市场信心受挫，避险情绪升温',
                'content': '市场遭遇大幅下跌，避险情绪明显上升...'
            }
        }
        
        if sentiment >= 0.5:
            return templates['very_positive']
        elif sentiment > 0:
            return templates['positive']
        elif sentiment > -0.5:
            return templates['negative']
        else:
            return templates['very_negative']
    
    def _get_company_news_template(self, performance):
        """获取公司新闻模板"""
        # TODO: 实现更多样化的新闻模板
        return {
            'title': '{company_name}股价表现引关注',
            'content': '{company_name}今日股价变动{price_change:.1%}，成交量变化{volume_change:.1%}...'
        }
    
    def _get_event_news_template(self, event_type):
        """获取事件新闻模板"""
        # TODO: 从数据库加载模板
        return {
            'title': '市场出现重要事件',
            'content': '市场发生{event.type}事件，影响程度{event.severity}...'
        }
    
    def _calculate_news_impact(self, action_type, action_data, impact_factors):
        """计算新闻影响度"""
        # TODO: 实现更复杂的影响度计算
        return random.randint(-2, 2) 