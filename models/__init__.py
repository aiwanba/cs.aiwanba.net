from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# 导入所有模型，确保它们被注册到 db
from .user import User
from .company import Company
from .stock import StockHolding, Transaction
from .bank import BankAccount, BankLoan, BankTransaction
from .news import NewsEvent, NewsComment
from .social import Team, TeamMember, TeamDiscussion, DiscussionComment, UserMessage
from .analysis import MarketAnalysis, CompanyAnalysis, TechnicalIndicator
from .ai_player import AIPlayer

# 初始化数据库
def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all() 