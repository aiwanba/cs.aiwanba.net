from apscheduler.schedulers.background import BackgroundScheduler
from services.interest import InterestService
from datetime import datetime

scheduler = BackgroundScheduler()

def init_scheduler():
    """初始化定时任务"""
    # 每天凌晨1点计算利息
    scheduler.add_job(
        InterestService.process_daily_interest,
        'cron',
        hour=1,
        minute=0
    )
    
    scheduler.start() 