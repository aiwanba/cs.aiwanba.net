def calculate_fee(amount: float) -> float:
    """计算交易手续费（费率0.3%）"""
    return round(amount * 0.003, 2) 