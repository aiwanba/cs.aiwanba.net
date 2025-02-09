import logging

class HealthCheckFilter(logging.Filter):
    """过滤健康检查日志"""
    def filter(self, record):
        return '/health' not in record.getMessage()

class StaticFileFilter(logging.Filter):
    """过滤静态文件日志"""
    def filter(self, record):
        return '/static/' not in record.getMessage()

class DuplicateFilter(logging.Filter):
    """过滤重复日志"""
    def __init__(self, interval=1):
        super().__init__()
        self.interval = interval
        self.last_log = {}
    
    def filter(self, record):
        current_time = record.created
        last_time = self.last_log.get(record.msg, 0)
        
        if current_time - last_time > self.interval:
            self.last_log[record.msg] = current_time
            return True
        return False 