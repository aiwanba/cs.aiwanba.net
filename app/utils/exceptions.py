class CustomAPIException(Exception):
    """自定义API异常基类"""
    def __init__(self, message, code=400, status=400):
        super().__init__()
        self.message = message
        self.code = code
        self.status = status

class CompanyError(CustomAPIException):
    """公司相关错误"""
    pass

class StockError(CustomAPIException):
    """股票相关错误"""
    pass

class BankError(CustomAPIException):
    """银行相关错误"""
    pass

class AuthenticationError(CustomAPIException):
    """认证相关错误"""
    def __init__(self, message="Authentication failed", code=401):
        super().__init__(message, code, 401) 