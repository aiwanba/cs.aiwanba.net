# 银行模块
class Bank:
    def __init__(self, name, capital):
        self.name = name  # 银行名称
        self.capital = capital  # 银行资金
        self.loans = {}  # 贷款信息 {公司ID: 贷款金额}

    def grant_loan(self, company_id, amount):
        """发放贷款"""
        if amount > self.capital:
            raise ValueError("贷款金额超过银行资金")
        self.loans[company_id] = self.loans.get(company_id, 0) + amount
        self.capital -= amount

    def repay_loan(self, company_id, amount):
        """偿还贷款"""
        if self.loans.get(company_id, 0) < amount:
            raise ValueError("还款金额超过贷款金额")
        self.loans[company_id] -= amount
        self.capital += amount

    def calculate_interest(self, company_id, rate, period):
        """计算贷款利息"""
        if company_id not in self.loans:
            raise ValueError("公司无贷款记录")
        principal = self.loans[company_id]
        return principal * rate * period

    def check_credit(self, company_id):
        """评估公司信用"""
        # 这里可以添加更复杂的信用评估逻辑
        loan_amount = self.loans.get(company_id, 0)
        if loan_amount > 1000000:
            return "C"
        elif loan_amount > 500000:
            return "B"
        else:
            return "A" 