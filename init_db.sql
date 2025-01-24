-- 创建用户表
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    balance DECIMAL(15,2) DEFAULT 100000.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 创建公司表
CREATE TABLE IF NOT EXISTS companies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    founder_id INT NOT NULL,
    total_shares INT DEFAULT 1000000,
    current_price DECIMAL(10,2) DEFAULT 10.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (founder_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 创建股票交易记录表
CREATE TABLE IF NOT EXISTS stock_transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    company_id INT NOT NULL,
    shares INT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    transaction_type ENUM('BUY', 'SELL') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (company_id) REFERENCES companies(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 创建索引优化查询性能
CREATE INDEX idx_transactions ON stock_transactions (user_id, company_id);
CREATE INDEX idx_companies ON companies (founder_id);

-- 创建银行交易记录表
CREATE TABLE IF NOT EXISTS bank_transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    operation_type ENUM('DEPOSIT', 'WITHDRAW') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 添加银行交易索引
CREATE INDEX idx_bank_trans ON bank_transactions (user_id, created_at);

-- 在文件末尾添加测试数据
INSERT INTO users (username, email, balance) VALUES
('test_user', 'test@aiwanba.net', 100000.00),
('ai_player1', 'ai1@aiwanba.net', 200000.00);

INSERT INTO companies (name, founder_id, current_price) VALUES
('测试科技', 1, 15.00),
('AI交易公司', 2, 20.00);

-- 添加用户余额视图
CREATE VIEW user_balance_view AS
SELECT id, username, balance 
FROM users
WHERE balance > 0;

-- 添加限价单表
CREATE TABLE IF NOT EXISTS limit_orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    company_id INT NOT NULL,
    shares INT NOT NULL,
    limit_price DECIMAL(10,2) NOT NULL,
    order_type ENUM('BUY', 'SELL') NOT NULL,
    status ENUM('OPEN', 'FILLED', 'CANCELLED') DEFAULT 'OPEN',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (company_id) REFERENCES companies(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 添加索引
CREATE INDEX idx_limit_orders ON limit_orders (company_id, limit_price, status);

-- 添加公司持股表
CREATE TABLE IF NOT EXISTS company_holdings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    holder_company_id INT NOT NULL,
    target_company_id INT NOT NULL,
    shares_held INT NOT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (holder_company_id) REFERENCES companies(id),
    FOREIGN KEY (target_company_id) REFERENCES companies(id),
    UNIQUE KEY unique_holding (holder_company_id, target_company_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 添加索引
CREATE INDEX idx_company_holdings ON company_holdings (holder_company_id, target_company_id);

-- 添加交易分析视图
CREATE VIEW trade_analysis_view AS
SELECT 
    DATE(created_at) AS trade_date,
    company_id,
    transaction_type,
    COUNT(*) AS trade_count,
    SUM(shares) AS total_shares,
    AVG(price) AS average_price
FROM stock_transactions
GROUP BY trade_date, company_id, transaction_type;

-- 添加订单撤销记录表
CREATE TABLE IF NOT EXISTS order_cancellations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    reason ENUM('USER_REQUEST', 'SYSTEM_CANCEL') NOT NULL,
    cancelled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES limit_orders(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 添加索引
CREATE INDEX idx_cancellations ON order_cancellations (order_id, cancelled_at);

-- 添加AI玩家表
CREATE TABLE IF NOT EXISTS ai_players (
    id INT AUTO_INCREMENT PRIMARY KEY,
    strategy_type ENUM('CONSERVATIVE', 'AGGRESSIVE', 'BALANCED') NOT NULL,
    initial_balance DECIMAL(15,2) DEFAULT 100000.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 添加AI操作记录表
CREATE TABLE IF NOT EXISTS ai_actions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ai_id INT NOT NULL,
    action_type ENUM('BUY', 'SELL', 'HOLD') NOT NULL,
    company_id INT,
    shares INT,
    price DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ai_id) REFERENCES ai_players(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4; 