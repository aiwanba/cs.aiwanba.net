-- 创建数据库
CREATE DATABASE IF NOT EXISTS cs_aiwanba_net CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE cs_aiwanba_net;

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(64) NOT NULL UNIQUE,
    password_hash VARCHAR(128) NOT NULL,
    email VARCHAR(120) UNIQUE,
    balance DECIMAL(10, 2) DEFAULT 0.00,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 公司表
CREATE TABLE IF NOT EXISTS companies (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    total_shares INT NOT NULL,
    available_shares INT NOT NULL,
    current_price DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 股票持有记录表
CREATE TABLE IF NOT EXISTS stock_holdings (
    id INT PRIMARY KEY AUTO_INCREMENT,
    holder_id INT NOT NULL,
    company_id INT NOT NULL,
    shares INT NOT NULL,
    purchase_price DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (holder_id) REFERENCES users(id),
    FOREIGN KEY (company_id) REFERENCES companies(id)
);

-- 交易记录表
CREATE TABLE IF NOT EXISTS transactions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    company_id INT NOT NULL,
    type ENUM('buy', 'sell') NOT NULL,
    shares INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (company_id) REFERENCES companies(id)
);

-- 银行账户表
CREATE TABLE IF NOT EXISTS bank_accounts (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    account_type ENUM('savings', 'loan') NOT NULL,
    balance DECIMAL(10, 2) NOT NULL,
    interest_rate DECIMAL(5, 4) NOT NULL,
    status ENUM('active', 'closed') DEFAULT 'active',
    start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_date TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 新闻表
CREATE TABLE IF NOT EXISTS news (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    type ENUM('market', 'company', 'system') NOT NULL,
    company_id INT NULL,
    impact DECIMAL(4, 2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id)
);

-- AI玩家表
CREATE TABLE IF NOT EXISTS ai_players (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(64) NOT NULL UNIQUE,
    balance DECIMAL(10, 2) DEFAULT 0.00,
    risk_preference DECIMAL(3, 2) NOT NULL,
    trading_frequency DECIMAL(3, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 创建管理员用户
INSERT INTO users (username, password_hash, email, is_admin, balance)
VALUES ('admin', 'pbkdf2:sha256:600000$dNwpVcGZJZGrYXQx$4fd90106b9279b6d86d78a0b82d83e5af3ecd83f98ecb9898d9f36a0ad894b34', 'admin@example.com', TRUE, 1000000.00);

-- 创建示例公司
INSERT INTO companies (name, description, total_shares, available_shares, current_price)
VALUES 
('科技创新股份', '专注于人工智能和机器学习技术研发', 1000000, 1000000, 10.00),
('绿色能源集团', '致力于可再生能源开发和应用', 800000, 800000, 15.00),
('医疗科技公司', '研发创新医疗设备和技术', 500000, 500000, 20.00);

-- 创建示例AI玩家
INSERT INTO ai_players (name, balance, risk_preference, trading_frequency)
VALUES 
('AI投资者Alpha', 100000.00, 0.7, 0.6),
('AI投资者Beta', 100000.00, 0.5, 0.4),
('AI投资者Gamma', 100000.00, 0.3, 0.8); 