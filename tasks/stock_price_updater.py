from apscheduler.schedulers.background import BackgroundScheduler
from services.stock_price_service import StockPriceService
from models import db
from datetime import datetime, timedelta
import pytz

# 设置时区
tz = pytz.timezone('Asia/Shanghai')

scheduler = BackgroundScheduler(timezone=tz)

def setup_stock_price_updater(app):
    """设置股票价格更新定时任务"""
    with app.app_context():
        # 每5分钟更新一次股票价格
        scheduler.add_job(
            func=update_stock_prices,
            trigger='interval',
            minutes=5,
            next_run_time=datetime.now(tz) + timedelta(seconds=10),
            args=[app]
        )
        scheduler.start()

def update_stock_prices(app):
    """更新股票价格"""
    with app.app_context():
        try:
            updated_count = StockPriceService.update_stock_prices()
            print(f"[{datetime.now(tz)}] 成功更新 {updated_count} 只股票价格")
        except Exception as e:
            print(f"[{datetime.now(tz)}] 更新股票价格失败: {str(e)}") 