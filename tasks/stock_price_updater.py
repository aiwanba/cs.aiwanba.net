from apscheduler.schedulers.background import BackgroundScheduler
from services.stock_price_service import StockPriceService
import logging
from pytz import timezone

logger = logging.getLogger(__name__)

def setup_stock_price_updater():
    """设置股票价格更新定时任务"""
    scheduler = BackgroundScheduler(timezone=timezone('Asia/Shanghai'))  # 设置时区为上海
    
    # 每分钟更新一次股票价格
    scheduler.add_job(
        update_stock_prices,
        'interval',
        minutes=1,
        id='stock_price_updater'
    )
    
    scheduler.start()
    logger.info("股票价格更新定时任务已启动")

def update_stock_prices():
    """更新所有股票价格的任务"""
    try:
        updates = StockPriceService.update_all_stock_prices()
        logger.info(f"已更新 {len(updates)} 支股票的价格")
    except Exception as e:
        logger.error(f"更新股票价格时发生错误: {str(e)}") 