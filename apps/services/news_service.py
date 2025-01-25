from datetime import datetime
from apps.models.news import News
from apps.models.company import Company
from app import db

class NewsService:
    @staticmethod
    def create_news(title, content, news_type, company_id=None, impact=0):
        """创建新闻"""
        news = News(
            title=title,
            content=content,
            type=news_type,
            company_id=company_id,
            impact=impact
        )
        
        db.session.add(news)
        db.session.commit()
        
        # 应用市场影响
        news.apply_market_effect()
        return news
    
    @staticmethod
    def get_news_list(news_type=None, company_id=None, limit=20):
        """获取新闻列表"""
        query = News.query.order_by(News.created_at.desc())
        
        if news_type:
            query = query.filter_by(type=news_type)
        if company_id:
            query = query.filter_by(company_id=company_id)
            
        return query.limit(limit).all()
    
    @staticmethod
    def generate_market_news():
        """生成市场新闻"""
        # 获取市场总值变化
        companies = Company.query.all()
        total_market_value = sum(c.market_value() for c in companies)
        
        # 生成市场动态新闻
        if total_market_value > 0:  # 实际应该与历史数据比较
            title = "市场持续走强"
            content = "市场总市值达到{:,.2f}元，投资者信心增强。".format(total_market_value)
            impact = 0.01
        else:
            title = "市场表现低迷"
            content = "市场总市值为{:,.2f}元，投资者保持观望。".format(total_market_value)
            impact = -0.01
            
        return NewsService.create_news(title, content, 'market', impact=impact)
    
    @staticmethod
    def generate_company_news(company):
        """生成公司新闻"""
        # 分析公司表现
        market_value = company.market_value()
        price_change = 0  # 实际应该与历史价格比较
        
        if price_change > 0:
            title = f"{company.name}股价上涨"
            content = f"{company.name}表现强劲，市值达到{market_value:,.2f}元。"
            impact = 0.02
        elif price_change < 0:
            title = f"{company.name}股价下跌"
            content = f"{company.name}表现低迷，市值降至{market_value:,.2f}元。"
            impact = -0.02
        else:
            title = f"{company.name}股价稳定"
            content = f"{company.name}运营稳定，市值维持在{market_value:,.2f}元。"
            impact = 0
            
        return NewsService.create_news(
            title, content, 'company',
            company_id=company.id, impact=impact
        ) 