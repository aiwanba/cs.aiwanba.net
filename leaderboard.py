from extensions import app, db
from models import User, Transaction

def get_leaderboard():
    """
    获取排行榜数据
    """
    with app.app_context():
        # 获取所有用户
        users = User.query.all()
        leaderboard = []

        for user in users:
            # 计算用户的总资产（余额 + 股票市值）
            total_assets = user.balance
            holdings = Transaction.query.filter_by(user_id=user.id, type='buy').all()
            for holding in holdings:
                stock = holding.stock
                total_assets += stock.price * holding.quantity

            leaderboard.append({
                'username': user.username,
                'total_assets': total_assets
            })

        # 按总资产从高到低排序
        leaderboard.sort(key=lambda x: x['total_assets'], reverse=True)
        return leaderboard 