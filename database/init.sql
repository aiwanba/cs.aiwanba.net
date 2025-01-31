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
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
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
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
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
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
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

-- 资金流水表
CREATE TABLE transactions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL COMMENT '用户ID',
    type TINYINT NOT NULL COMMENT '类型：1-创建公司，2-创建银行，3-存款，4-取款，5-贷款，6-还款',
    amount DECIMAL(20,2) NOT NULL COMMENT '金额',
    balance DECIMAL(20,2) NOT NULL COMMENT '变动后余额',
    related_id BIGINT COMMENT '关联ID',
    description VARCHAR(200) COMMENT '说明',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
) COMMENT '资金流水表';

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

-- 触发器部分整理
DELIMITER $$

-- 存款前检查用户资金
CREATE TRIGGER before_deposit_insert
BEFORE INSERT ON deposits
FOR EACH ROW
BEGIN
    DECLARE user_cash DECIMAL(20,2);
    SELECT cash INTO user_cash FROM users WHERE id = NEW.user_id;
    IF user_cash < NEW.amount THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '用户现金不足';
    END IF;
    -- 如果资金充足，更新用户现金
    UPDATE users SET cash = cash - NEW.amount WHERE id = NEW.user_id;
END$$

-- 存款后更新银行存款总额和记录资金流水
CREATE TRIGGER after_deposit_insert
AFTER INSERT ON deposits
FOR EACH ROW
BEGIN
    -- 更新银行存款总额
    UPDATE banks 
    SET total_deposit = total_deposit + NEW.amount,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = NEW.bank_id;
    
    -- 创建存款资金流水记录
    INSERT INTO transactions (
        user_id, type, amount, balance, related_id, description
    )
    SELECT 
        NEW.user_id,
        3, -- 存款类型
        -NEW.amount,
        users.cash,
        NEW.id,
        CONCAT('存款：', NEW.amount, '元，期限', NEW.term, '天，利率', NEW.interest_rate, '%')
    FROM users
    WHERE id = NEW.user_id;
END$$

-- 存款支取时更新银行存款总额和记录资金流水
CREATE TRIGGER after_deposit_update
AFTER UPDATE ON deposits
FOR EACH ROW
BEGIN
    IF NEW.status = 2 AND OLD.status = 1 THEN
        -- 更新银行存款总额
        UPDATE banks 
        SET total_deposit = total_deposit - OLD.amount,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = OLD.bank_id;
        
        -- 返还用户现金
        UPDATE users 
        SET cash = cash + OLD.amount 
        WHERE id = OLD.user_id;
        
        -- 创建取款资金流水记录
        INSERT INTO transactions (
            user_id, type, amount, balance, related_id, description
        )
        SELECT 
            OLD.user_id,
            4, -- 取款类型
            OLD.amount,
            users.cash,
            OLD.id,
            CONCAT('取款：', OLD.amount, '元')
        FROM users
        WHERE id = OLD.user_id;
    END IF;
END$$

-- 贷款后更新银行贷款总额和记录资金流水
CREATE TRIGGER after_loan_insert
AFTER INSERT ON loans
FOR EACH ROW
BEGIN
    -- 更新银行贷款总额
    UPDATE banks 
    SET total_loan = total_loan + NEW.amount,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = NEW.bank_id;
    
    -- 更新用户现金
    UPDATE users 
    SET cash = cash + NEW.amount 
    WHERE id = NEW.user_id;
    
    -- 创建贷款资金流水记录
    INSERT INTO transactions (
        user_id, type, amount, balance, related_id, description
    )
    SELECT 
        NEW.user_id,
        5, -- 贷款类型
        NEW.amount,
        users.cash,
        NEW.id,
        CONCAT('贷款：', NEW.amount, '元，期限', NEW.term, '天，利率', NEW.interest_rate, '%')
    FROM users
    WHERE id = NEW.user_id;
END$$

-- 贷款还款时更新银行贷款总额和记录资金流水
CREATE TRIGGER after_loan_update
AFTER UPDATE ON loans
FOR EACH ROW
BEGIN
    IF NEW.status = 2 AND OLD.status = 1 THEN
        -- 更新银行贷款总额
        UPDATE banks 
        SET total_loan = total_loan - OLD.amount,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = OLD.bank_id;
        
        -- 扣减用户现金
        UPDATE users 
        SET cash = cash - OLD.amount 
        WHERE id = OLD.user_id;
        
        -- 创建还款资金流水记录
        INSERT INTO transactions (
            user_id, type, amount, balance, related_id, description
        )
        SELECT 
            OLD.user_id,
            6, -- 还款类型
            -OLD.amount,
            users.cash,
            OLD.id,
            CONCAT('还款：', OLD.amount, '元')
        FROM users
        WHERE id = OLD.user_id;
    END IF;
END$$

DELIMITER ;