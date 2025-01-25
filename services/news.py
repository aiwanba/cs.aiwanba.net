from models import db, NewsEvent, NewsComment, Company
from datetime import datetime, timedelta
import random

class NewsService:
    """新闻服务"""
    
    @staticmethod
    def create_news(title, content, type, impact_type=None, impact_value=None, 
                   company_id=None, duration_hours=24):
        """创建新闻"""
        news = NewsEvent(
            title=title,
            content=content,
            type=type,
            impact_type=impact_type,
            impact_value=impact_value,
            company_id=company_id,
            end_time=datetime.now() + timedelta(hours=duration_hours)
        )
        
        try:
            db.session.add(news)
            db.session.commit()
            return True, news
        except Exception as e:
            db.session.rollback()
            return False, str(e)
    
    @staticmethod
    def get_active_news():
        """获取当前生效的新闻"""
        now = datetime.now()
        return NewsEvent.query.filter(
            NewsEvent.active == True,
            NewsEvent.start_time <= now,
            (NewsEvent.end_time.is_(None) | (NewsEvent.end_time >= now))
        ).order_by(NewsEvent.created_at.desc()).all()
    
    @staticmethod
    def get_company_news(company_id):
        """获取公司相关新闻"""
        return NewsEvent.query.filter_by(
            company_id=company_id,
            active=True
        ).order_by(NewsEvent.created_at.desc()).all()
    
    @staticmethod
    def add_comment(news_id, user_id, content):
        """添加新闻评论"""
        comment = NewsComment(
            news_id=news_id,
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
    def generate_market_news():
        """生成市场新闻（每日运行）"""
        # 市场趋势新闻模板
        trend_templates = [
            {
                'title': '市场信心上升，多只股票呈上涨趋势',
                'content': '今日市场整体表现积极，投资者信心明显提升。分析师认为，这与近期经济数据向好有关。',
                'impact': 0.02  # 上涨2%
            },
            {
                'title': '市场观望情绪浓厚，成交量明显下降',
                'content': '今日市场交投清淡，多数投资者持观望态度。分析师指出，市场可能需要新的利好刺激。',
                'impact': -0.01  # 下跌1%
            }
        ]
        
        # 随机选择一个模板
        template = random.choice(trend_templates)
        
        # 创建新闻
        success, news = NewsService.create_news(
            title=template['title'],
            content=template['content'],
            type='market',
            impact_type='price',
            impact_value=template['impact']
        )
        
        if success:
            # 影响市场价格
            companies = Company.query.all()
            for company in companies:
                company.current_price *= (1 + template['impact'])
            db.session.commit()
            
        return success, news
    
    @staticmethod
    def apply_news_effects():
        """应用新闻效果（定时运行）"""
        active_news = NewsService.get_active_news()
        
        for news in active_news:
            if news.impact_type and news.impact_value:
                if news.type == 'company' and news.company_id:
                    # 影响单个公司
                    company = Company.query.get(news.company_id)
                    if company:
                        if news.impact_type == 'price':
                            company.current_price *= (1 + news.impact_value)
                        # 可以添加其他类型的影响...
                
                elif news.type == 'market':
                    # 影响所有公司
                    companies = Company.query.all()
                    for company in companies:
                        if news.impact_type == 'price':
                            company.current_price *= (1 + news.impact_value)
                        # 可以添加其他类型的影响...
                
                elif news.type == 'bank':
                    # 影响银行利率等...
                    pass
        
        db.session.commit() 