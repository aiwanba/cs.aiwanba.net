from extensions import app, db
from models import Stock
import random
import time

# 新闻事件列表
NEWS_EVENTS = [
    "公司发布新产品，市场反应热烈",
    "公司财报超出预期，股价上涨",
    "行业政策利好，相关股票受益",
    "经济指标不佳，市场整体下跌",
    "公司高管辞职，股价波动",
    "公司被收购，股价大幅上涨",
    "公司陷入丑闻，股价暴跌",
    "行业竞争加剧，相关股票承压",
    "全球经济复苏，市场整体上涨",
    "公司宣布分红，股价小幅上涨"
]

def generate_news_event():
    """
    生成随机新闻事件并影响股票价格
    """
    with app.app_context():
        # 随机选择一支股票
        stock = random.choice(Stock.query.all())
        if not stock:
            return

        # 随机选择一个新闻事件
        event = random.choice(NEWS_EVENTS)
        print(f"新闻事件: {stock.name} - {event}")

        # 根据新闻事件调整股票价格
        if "上涨" in event:
            stock.price *= 1.1  # 价格上涨10%
        elif "下跌" in event:
            stock.price *= 0.9  # 价格下跌10%
        elif "波动" in event:
            stock.price *= 1.05  # 价格上涨5%

        # 保存价格变动
        db.session.add(stock)
        db.session.commit()

def start_news_simulation():
    """
    启动新闻事件模拟
    """
    while True:
        generate_news_event()
        time.sleep(300)  # 每5分钟生成一次新闻事件 