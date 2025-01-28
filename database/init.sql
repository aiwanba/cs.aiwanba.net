-- 创建数据库
CREATE DATABASE IF NOT EXISTS cs_aiwanba_net DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE cs_aiwanba_net;

-- 用户表
CREATE TABLE users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL COMMENT '用户名',
    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希',
    email VARCHAR(100) UNIQUE NOT NULL COMMENT '邮箱',
    cash DECIMAL(20,2) DEFAULT 10000000.00 COMMENT '现金余额',
    is_admin TINYINT DEFAULT 0 COMMENT '是否管理员：0-否，1-是',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    status TINYINT DEFAULT 1 COMMENT '状态：1-正常，0-禁用'
) COMMENT '用户表';

-- 公司表
CREATE TABLE companies (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) UNIQUE NOT NULL COMMENT '公司名称',
    stock_code VARCHAR(6) UNIQUE NOT NULL COMMENT '股票代码',
    industry VARCHAR(50) NOT NULL COMMENT '行业分类',
    total_shares BIGINT NOT NULL COMMENT '总股本',
    circulating_shares BIGINT NOT NULL COMMENT '流通股本',
    initial_price DECIMAL(10,2) NOT NULL COMMENT '发行价',
    current_price DECIMAL(10,2) NOT NULL COMMENT '当前股价',
    cash_balance DECIMAL(20,2) NOT NULL COMMENT '公司现金',
    founder_id BIGINT NOT NULL COMMENT '创始人ID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    status TINYINT DEFAULT 1 COMMENT '状态：1-正常，2-停牌，0-破产',
    FOREIGN KEY (founder_id) REFERENCES users(id)
) COMMENT '公司表';

-- 股权表
CREATE TABLE shareholdings (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    company_id BIGINT NOT NULL COMMENT '公司ID',
    user_id BIGINT NOT NULL COMMENT '股东ID',
    shares BIGINT NOT NULL COMMENT '持股数量',
    cost_price DECIMAL(10,2) NOT NULL COMMENT '成本价',
    pledged_shares BIGINT DEFAULT 0 COMMENT '质押股份数',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE KEY `unique_holding` (company_id, user_id)
) COMMENT '股权表';

-- 银行表
CREATE TABLE banks (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) UNIQUE NOT NULL COMMENT '银行名称',
    owner_id BIGINT NOT NULL COMMENT '所有者ID',
    capital DECIMAL(20,2) NOT NULL COMMENT '注册资本',
    reserve_ratio DECIMAL(5,2) DEFAULT 10.00 COMMENT '准备金率',
    deposit_rate DECIMAL(5,2) NOT NULL COMMENT '存款利率',
    loan_rate DECIMAL(5,2) NOT NULL COMMENT '贷款利率',
    total_deposit DECIMAL(20,2) DEFAULT 0 COMMENT '存款总额',
    total_loan DECIMAL(20,2) DEFAULT 0 COMMENT '贷款总额',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    status TINYINT DEFAULT 1 COMMENT '状态：1-正常，0-破产',
    FOREIGN KEY (owner_id) REFERENCES users(id)
) COMMENT '银行表';

-- 存款表
CREATE TABLE deposits (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    bank_id BIGINT NOT NULL COMMENT '银行ID',
    user_id BIGINT NOT NULL COMMENT '用户ID',
    amount DECIMAL(20,2) NOT NULL COMMENT '存款金额',
    interest_rate DECIMAL(5,2) NOT NULL COMMENT '利率',
    term INT NOT NULL COMMENT '期限(天)',
    start_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '开始日期',
    end_date TIMESTAMP NULL COMMENT '到期日期',
    status TINYINT DEFAULT 1 COMMENT '状态：1-正常，2-已支取，0-违约',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (bank_id) REFERENCES banks(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
) COMMENT '存款表';

-- 贷款表
CREATE TABLE loans (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    bank_id BIGINT NOT NULL COMMENT '银行ID',
    user_id BIGINT NOT NULL COMMENT '借款人ID',
    amount DECIMAL(20,2) NOT NULL COMMENT '贷款金额',
    interest_rate DECIMAL(5,2) NOT NULL COMMENT '利率',
    term INT NOT NULL COMMENT '期限(天)',
    start_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '放款日期',
    end_date TIMESTAMP NULL COMMENT '到期日期',
    collateral_type TINYINT COMMENT '抵押品类型：1-股票，2-存单',
    collateral_id BIGINT COMMENT '抵押品ID',
    status TINYINT DEFAULT 1 COMMENT '状态：1-正常，2-已还清，0-违约',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (bank_id) REFERENCES banks(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
) COMMENT '贷款表';

-- 交易订单表
CREATE TABLE orders (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    company_id BIGINT NOT NULL COMMENT '公司ID',
    user_id BIGINT NOT NULL COMMENT '用户ID',
    order_type TINYINT NOT NULL COMMENT '订单类型：1-买入，2-卖出',
    price_type TINYINT NOT NULL COMMENT '价格类型：1-市价，2-限价',
    price DECIMAL(10,2) COMMENT '委托价格',
    quantity BIGINT NOT NULL COMMENT '委托数量',
    filled_quantity BIGINT DEFAULT 0 COMMENT '已成交数量',
    status TINYINT DEFAULT 1 COMMENT '状态：1-未成交，2-部分成交，3-全部成交，4-已撤销',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
) COMMENT '交易订单表';

-- 成交记录表
CREATE TABLE trades (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    company_id BIGINT NOT NULL COMMENT '公司ID',
    buy_order_id BIGINT NOT NULL COMMENT '买方订单ID',
    sell_order_id BIGINT NOT NULL COMMENT '卖方订单ID',
    price DECIMAL(10,2) NOT NULL COMMENT '成交价格',
    quantity BIGINT NOT NULL COMMENT '成交数量',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id),
    FOREIGN KEY (buy_order_id) REFERENCES orders(id),
    FOREIGN KEY (sell_order_id) REFERENCES orders(id)
) COMMENT '成交记录表';

-- 消息表
CREATE TABLE messages (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    type TINYINT NOT NULL COMMENT '消息类型：1-系统公告，2-公司公告，3-交易提醒，4-风险预警',
    title VARCHAR(200) NOT NULL COMMENT '标题',
    content TEXT NOT NULL COMMENT '内容',
    related_id BIGINT COMMENT '关联ID',
    priority TINYINT DEFAULT 3 COMMENT '优先级：1-高，2-中，3-低',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expire_at TIMESTAMP NULL COMMENT '过期时间',
    status TINYINT DEFAULT 1 COMMENT '状态：1-有效，0-已过期'
) COMMENT '消息表';

-- 消息接收表
CREATE TABLE message_recipients (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    message_id BIGINT NOT NULL COMMENT '消息ID',
    user_id BIGINT NOT NULL COMMENT '接收用户ID',
    is_read TINYINT DEFAULT 0 COMMENT '是否已读：0-未读，1-已读',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (message_id) REFERENCES messages(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
) COMMENT '消息接收表';

-- 创建必要的索引
CREATE INDEX idx_companies_stock_code ON companies(stock_code);
CREATE INDEX idx_shareholdings_user ON shareholdings(user_id);
CREATE INDEX idx_orders_user ON orders(user_id);
CREATE INDEX idx_trades_company ON trades(company_id);
CREATE INDEX idx_messages_type ON messages(type);
CREATE INDEX idx_message_recipients_user ON message_recipients(user_id);

-- 触发器：更新公司股价
DELIMITER //
CREATE TRIGGER after_trade_insert
AFTER INSERT ON trades
FOR EACH ROW
BEGIN
    UPDATE companies 
    SET current_price = NEW.price,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = NEW.company_id;
END//
DELIMITER ;

-- 插入测试数据

-- 创建管理员用户
INSERT INTO users (username, password_hash, email, is_admin, cash) VALUES 
('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewLxGQoWWEqhUyGS', 'admin@test.com', 1, 10000000.00);
-- 密码: admin123

-- 创建测试用户
INSERT INTO users (username, password_hash, email, cash) VALUES 
('test1', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewLxGQoWWEqhUyGS', 'test1@test.com', 10000000.00),
('test2', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewLxGQoWWEqhUyGS', 'test2@test.com', 10000000.00);
-- 密码: test123

-- 创建示例公司
INSERT INTO companies (name, stock_code, industry, total_shares, circulating_shares, initial_price, current_price, cash_balance, founder_id) VALUES 
('腾讯科技', '000001', '互联网', 1000000000, 1000000000, 100.00, 100.00, 1000000000.00, 1),
('阿里巴巴', '000002', '电商', 1000000000, 1000000000, 88.88, 88.88, 1000000000.00, 1);

-- 创建初始持股记录
INSERT INTO shareholdings (company_id, user_id, shares, cost_price) VALUES 
(1, 1, 500000000, 100.00),  -- admin持有腾讯50%股份
(1, 2, 100000000, 100.00),  -- test1持有腾讯10%股份
(2, 1, 600000000, 88.88),   -- admin持有阿里60%股份
(2, 3, 100000000, 88.88);   -- test2持有阿里10%股份

-- 创建示例银行
INSERT INTO banks (name, owner_id, capital, deposit_rate, loan_rate) VALUES 
('中国银行', 1, 10000000000.00, 3.00, 6.00);

-- 创建示例存款
INSERT INTO deposits (bank_id, user_id, amount, interest_rate, term, start_date, end_date) VALUES 
(1, 2, 1000000.00, 3.00, 365, CURRENT_TIMESTAMP, DATE_ADD(CURRENT_TIMESTAMP, INTERVAL 365 DAY)),
(1, 3, 2000000.00, 3.00, 180, CURRENT_TIMESTAMP, DATE_ADD(CURRENT_TIMESTAMP, INTERVAL 180 DAY));

-- 创建示例贷款
INSERT INTO loans (bank_id, user_id, amount, interest_rate, term, start_date, end_date, collateral_type, collateral_id) VALUES 
(1, 2, 500000.00, 6.00, 365, CURRENT_TIMESTAMP, DATE_ADD(CURRENT_TIMESTAMP, INTERVAL 365 DAY), 1, 1);  -- 以腾讯股票为抵押

-- 创建示例交易订单
INSERT INTO orders (company_id, user_id, order_type, price_type, price, quantity, status) VALUES 
(1, 2, 1, 2, 101.00, 10000, 1),    -- test1要买入腾讯股票
(1, 3, 2, 2, 99.00, 20000, 1),     -- test2要卖出腾讯股票
(2, 2, 1, 2, 89.00, 15000, 1),     -- test1要买入阿里股票
(2, 1, 2, 2, 90.00, 25000, 1);     -- admin要卖出阿里股票

-- 创建系统公告
INSERT INTO messages (type, title, content, priority, expire_at) VALUES 
(1, '系统上线公告', '欢迎使用股票交易游戏系统！', 1, DATE_ADD(CURRENT_TIMESTAMP, INTERVAL 30 DAY)),
(1, '系统使用指南', '1. 注册登录\n2. 查看股票\n3. 开始交易', 2, DATE_ADD(CURRENT_TIMESTAMP, INTERVAL 30 DAY)),
(2, '腾讯科技公告', '公司第一季度业绩预告', 2, DATE_ADD(CURRENT_TIMESTAMP, INTERVAL 7 DAY)),
(2, '阿里巴巴公告', '关于股东大会的通知', 2, DATE_ADD(CURRENT_TIMESTAMP, INTERVAL 14 DAY));

-- 创建公告接收记录
INSERT INTO message_recipients (message_id, user_id) 
SELECT m.id, u.id 
FROM messages m 
CROSS JOIN users u;

-- 更新股权质押记录（对应贷款的抵押品）
UPDATE shareholdings 
SET pledged_shares = 50000000  -- 质押5000万股
WHERE company_id = 1 AND user_id = 2;  -- test1的腾讯股票

-- 创建一些成交记录
INSERT INTO trades (company_id, buy_order_id, sell_order_id, price, quantity, created_at) VALUES 
(1, 1, 2, 100.00, 5000, DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 1 DAY)),  -- 腾讯股票交易
(2, 3, 4, 89.50, 10000, DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 2 DAY));  -- 阿里股票交易

-- 更新订单的已成交数量和状态
UPDATE orders 
SET filled_quantity = 5000, status = 2  -- 部分成交
WHERE id = 1 OR id = 2;

UPDATE orders 
SET filled_quantity = 10000, status = 2  -- 部分成交
WHERE id = 3 OR id = 4;

-- 更新公司现金余额（根据交易情况）
UPDATE companies 
SET cash_balance = cash_balance + (5000 * 100.00)  -- 增加交易金额
WHERE id = 1;  -- 腾讯

UPDATE companies 
SET cash_balance = cash_balance + (10000 * 89.50)  -- 增加交易金额
WHERE id = 2;  -- 阿里

-- 更新用户现金余额（根据交易情况）
UPDATE users 
SET cash = cash - (5000 * 100.00)  -- 减去买入支出
WHERE id = 2;  -- test1

UPDATE users 
SET cash = cash + (5000 * 100.00)  -- 增加卖出收入
WHERE id = 3;  -- test2

UPDATE users 
SET cash = cash - (10000 * 89.50)  -- 减去买入支出
WHERE id = 2;  -- test1

UPDATE users 
SET cash = cash + (10000 * 89.50)  -- 增加卖出收入
WHERE id = 1;  -- admin 