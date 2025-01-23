-- 创建 companies 表
CREATE TABLE IF NOT EXISTS companies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL, -- 公司名称
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- 创建时间
    owner_id INT, -- 所属玩家 ID
    initial_capital DECIMAL(15, 2) NOT NULL -- 初始资金
);

-- 创建 stocks 表
CREATE TABLE IF NOT EXISTS stocks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT NOT NULL, -- 公司 ID
    player_id INT NOT NULL, -- 玩家 ID
    quantity INT NOT NULL, -- 股票数量
    price DECIMAL(15, 2) NOT NULL, -- 股票价格
    transaction_type ENUM('buy', 'sell') NOT NULL, -- 交易类型（买入/卖出）
    transaction_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- 交易时间
);

-- 创建 accounts 表
CREATE TABLE IF NOT EXISTS accounts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT NOT NULL, -- 公司 ID
    balance DECIMAL(15, 2) NOT NULL -- 账户余额
);

-- 创建 transactions 表
CREATE TABLE IF NOT EXISTS transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    account_id INT NOT NULL, -- 账户 ID
    transaction_type ENUM('deposit', 'withdraw', 'transfer') NOT NULL, -- 交易类型
    amount DECIMAL(15, 2) NOT NULL, -- 交易金额
    transaction_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- 交易时间
);

-- 创建 ai_players 表
CREATE TABLE IF NOT EXISTS ai_players (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL, -- AI 玩家名称
    strategy ENUM('conservative', 'aggressive', 'balanced') NOT NULL, -- 交易策略
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- 创建时间
);

-- 创建 ai_transactions 表
CREATE TABLE IF NOT EXISTS ai_transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ai_player_id INT NOT NULL, -- AI 玩家 ID
    company_id INT NOT NULL, -- 公司 ID
    quantity INT NOT NULL, -- 交易数量
    price DECIMAL(15, 2) NOT NULL, -- 交易价格
    transaction_type ENUM('buy', 'sell') NOT NULL, -- 交易类型（买入/卖出）
    transaction_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- 交易时间
); 