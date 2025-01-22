CREATE DATABASE IF NOT EXISTS cs_aiwanba_net;

USE cs_aiwanba_net;

CREATE TABLE IF NOT EXISTS company (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    balance FLOAT NOT NULL,
    is_ai BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS transaction (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT NOT NULL,
    asset_type ENUM('stock', 'futures', 'forex') NOT NULL DEFAULT 'stock',
    target_company_id INT NOT NULL,
    quantity INT NOT NULL,
    price FLOAT NOT NULL,
    transaction_type ENUM('buy', 'sell') NOT NULL,
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES company(id),
    FOREIGN KEY (target_company_id) REFERENCES company(id)
);

CREATE TABLE IF NOT EXISTS stock_holding (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT NOT NULL,
    target_company_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 0,
    FOREIGN KEY (company_id) REFERENCES company(id),
    FOREIGN KEY (target_company_id) REFERENCES company(id)
);

-- 创建市场数据表
CREATE TABLE IF NOT EXISTS market_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT NOT NULL,
    open_price FLOAT NOT NULL,
    close_price FLOAT NOT NULL,
    high_price FLOAT NOT NULL,
    low_price FLOAT NOT NULL,
    volume INT NOT NULL,
    date DATE NOT NULL,
    FOREIGN KEY (company_id) REFERENCES company(id)
);

-- 创建贷款表
CREATE TABLE IF NOT EXISTS loan (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT NOT NULL,
    amount FLOAT NOT NULL,
    interest_rate FLOAT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status ENUM('active', 'paid') NOT NULL,
    FOREIGN KEY (company_id) REFERENCES company(id)
);

-- 创建公司业绩报表表
CREATE TABLE IF NOT EXISTS company_report (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT NOT NULL,
    revenue FLOAT NOT NULL,
    profit FLOAT NOT NULL,
    assets FLOAT NOT NULL,
    liabilities FLOAT NOT NULL,
    report_date DATE NOT NULL,
    FOREIGN KEY (company_id) REFERENCES company(id)
);

-- 创建订单簿表
CREATE TABLE IF NOT EXISTS order_book (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT NOT NULL,  -- 下单公司
    target_company_id INT NOT NULL,  -- 目标公司股票
    order_type ENUM('buy', 'sell') NOT NULL,
    price FLOAT NOT NULL,
    quantity INT NOT NULL,
    remaining_quantity INT NOT NULL,  -- 未成交数量
    status ENUM('pending', 'partial', 'filled', 'cancelled') NOT NULL,
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES company(id),
    FOREIGN KEY (target_company_id) REFERENCES company(id)
);

-- 创建初始股票发行表
CREATE TABLE IF NOT EXISTS stock_issue (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT NOT NULL,
    total_shares INT NOT NULL,  -- 总股本
    circulating_shares INT NOT NULL,  -- 流通股数
    issue_price FLOAT NOT NULL,  -- 发行价格
    issue_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES company(id)
); 