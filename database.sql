-- 创建数据库
CREATE DATABASE IF NOT EXISTS cs_aiwanba_net DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE cs_aiwanba_net;

-- 用户表
CREATE TABLE `users` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '用户ID',
    `username` VARCHAR(50) NOT NULL COMMENT '用户名',
    `password` VARCHAR(255) NOT NULL COMMENT '密码(加密存储)',
    `nickname` VARCHAR(50) NOT NULL COMMENT '昵称',
    `avatar` VARCHAR(255) DEFAULT NULL COMMENT '头像URL',
    `email` VARCHAR(100) NOT NULL COMMENT '邮箱',
    `phone` VARCHAR(20) DEFAULT NULL COMMENT '手机号',
    `balance` DECIMAL(20,2) DEFAULT 0.00 COMMENT '现金余额',
    `status` TINYINT DEFAULT 1 COMMENT '状态(0:禁用,1:正常)',
    `is_ai` TINYINT DEFAULT 0 COMMENT '是否是AI用户(0:否,1:是)',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `idx_username` (`username`),
    UNIQUE KEY `idx_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- 公司表
CREATE TABLE `companies` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '公司ID',
    `name` VARCHAR(100) NOT NULL COMMENT '公司名称',
    `code` VARCHAR(10) NOT NULL COMMENT '股票代码',
    `description` TEXT COMMENT '公司简介',
    `industry` VARCHAR(50) NOT NULL COMMENT '所属行业',
    `registered_capital` DECIMAL(20,2) NOT NULL COMMENT '注册资本',
    `total_shares` BIGINT NOT NULL COMMENT '总股本',
    `current_price` DECIMAL(10,2) DEFAULT 0.00 COMMENT '当前股价',
    `market_value` DECIMAL(20,2) DEFAULT 0.00 COMMENT '市值',
    `creator_id` BIGINT UNSIGNED NOT NULL COMMENT '创建者ID',
    `status` TINYINT DEFAULT 1 COMMENT '状态(0:退市,1:正常,2:停牌)',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `idx_code` (`code`),
    KEY `idx_creator` (`creator_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='公司表';

-- 股票持仓表
CREATE TABLE `stock_holdings` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '持仓ID',
    `user_id` BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
    `company_id` BIGINT UNSIGNED NOT NULL COMMENT '公司ID',
    `shares` BIGINT NOT NULL COMMENT '持有股数',
    `average_cost` DECIMAL(10,2) NOT NULL COMMENT '平均成本',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `idx_user_company` (`user_id`, `company_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='股票持仓表';

-- 交易订单表
CREATE TABLE `trade_orders` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '订单ID',
    `user_id` BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
    `company_id` BIGINT UNSIGNED NOT NULL COMMENT '公司ID',
    `type` TINYINT NOT NULL COMMENT '订单类型(1:买入,2:卖出)',
    `price` DECIMAL(10,2) NOT NULL COMMENT '委托价格',
    `shares` BIGINT NOT NULL COMMENT '委托股数',
    `status` TINYINT DEFAULT 0 COMMENT '状态(0:待成交,1:部分成交,2:全部成交,3:已取消)',
    `dealt_shares` BIGINT DEFAULT 0 COMMENT '已成交股数',
    `dealt_amount` DECIMAL(20,2) DEFAULT 0.00 COMMENT '已成交金额',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    KEY `idx_user` (`user_id`),
    KEY `idx_company` (`company_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='交易订单表';

-- 交易记录表
CREATE TABLE `trade_records` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '记录ID',
    `buyer_order_id` BIGINT UNSIGNED NOT NULL COMMENT '买方订单ID',
    `seller_order_id` BIGINT UNSIGNED NOT NULL COMMENT '卖方订单ID',
    `company_id` BIGINT UNSIGNED NOT NULL COMMENT '公司ID',
    `price` DECIMAL(10,2) NOT NULL COMMENT '成交价格',
    `shares` BIGINT NOT NULL COMMENT '成交股数',
    `amount` DECIMAL(20,2) NOT NULL COMMENT '成交金额',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    KEY `idx_buyer_order` (`buyer_order_id`),
    KEY `idx_seller_order` (`seller_order_id`),
    KEY `idx_company` (`company_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='交易记录表';

-- 银行账户表
CREATE TABLE `bank_accounts` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '账户ID',
    `user_id` BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
    `account_type` TINYINT NOT NULL COMMENT '账户类型(1:活期,2:定期)',
    `balance` DECIMAL(20,2) DEFAULT 0.00 COMMENT '账户余额',
    `interest_rate` DECIMAL(5,2) DEFAULT 0.00 COMMENT '年利率(%)',
    `maturity_date` DATE DEFAULT NULL COMMENT '到期日(定期)',
    `status` TINYINT DEFAULT 1 COMMENT '状态(0:冻结,1:正常)',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    KEY `idx_user` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='银行账户表';

-- 贷款表
CREATE TABLE `loans` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '贷款ID',
    `user_id` BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
    `amount` DECIMAL(20,2) NOT NULL COMMENT '贷款金额',
    `interest_rate` DECIMAL(5,2) NOT NULL COMMENT '年利率(%)',
    `term` INT NOT NULL COMMENT '贷款期限(月)',
    `monthly_payment` DECIMAL(20,2) NOT NULL COMMENT '月供金额',
    `remaining_amount` DECIMAL(20,2) NOT NULL COMMENT '剩余待还',
    `status` TINYINT DEFAULT 0 COMMENT '状态(0:审核中,1:已放款,2:已还清,3:拒绝,4:逾期)',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    KEY `idx_user` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='贷款表';

-- 新闻表
CREATE TABLE `news` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '新闻ID',
    `title` VARCHAR(200) NOT NULL COMMENT '新闻标题',
    `content` TEXT NOT NULL COMMENT '新闻内容',
    `type` TINYINT NOT NULL COMMENT '类型(1:系统新闻,2:公司公告,3:市场动态)',
    `company_id` BIGINT UNSIGNED DEFAULT NULL COMMENT '相关公司ID',
    `impact_score` INT DEFAULT 0 COMMENT '影响力评分',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    KEY `idx_company` (`company_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='新闻表';

-- AI策略表
CREATE TABLE `ai_strategies` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '策略ID',
    `ai_user_id` BIGINT UNSIGNED NOT NULL COMMENT 'AI用户ID',
    `strategy_type` TINYINT NOT NULL COMMENT '策略类型(1:保守,2:稳健,3:激进)',
    `risk_level` TINYINT NOT NULL COMMENT '风险等级(1-5)',
    `min_price` DECIMAL(10,2) DEFAULT NULL COMMENT '最低买入价',
    `max_price` DECIMAL(10,2) DEFAULT NULL COMMENT '最高买入价',
    `position_limit` INT DEFAULT 100 COMMENT '持仓上限(%)',
    `status` TINYINT DEFAULT 1 COMMENT '状态(0:禁用,1:启用)',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    KEY `idx_ai_user` (`ai_user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='AI策略表';

-- 聊天消息表
CREATE TABLE `chat_messages` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '消息ID',
    `sender_id` BIGINT UNSIGNED NOT NULL COMMENT '发送者ID',
    `receiver_id` BIGINT UNSIGNED DEFAULT NULL COMMENT '接收者ID(NULL表示群发)',
    `content` TEXT NOT NULL COMMENT '消息内容',
    `type` TINYINT NOT NULL COMMENT '消息类型(1:文本,2:图片,3:表情)',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    KEY `idx_sender` (`sender_id`),
    KEY `idx_receiver` (`receiver_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='聊天消息表';

-- 团队表
CREATE TABLE `teams` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '团队ID',
    `name` VARCHAR(50) NOT NULL COMMENT '团队名称',
    `leader_id` BIGINT UNSIGNED NOT NULL COMMENT '队长ID',
    `description` VARCHAR(200) DEFAULT NULL COMMENT '团队描述',
    `member_limit` INT DEFAULT 10 COMMENT '成员上限',
    `status` TINYINT DEFAULT 1 COMMENT '状态(0:解散,1:正常)',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    KEY `idx_leader` (`leader_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='团队表';

-- 团队成员表
CREATE TABLE `team_members` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '记录ID',
    `team_id` BIGINT UNSIGNED NOT NULL COMMENT '团队ID',
    `user_id` BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
    `role` TINYINT DEFAULT 0 COMMENT '角色(0:成员,1:管理员)',
    `contribution` DECIMAL(20,2) DEFAULT 0.00 COMMENT '贡献值',
    `joined_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '加入时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `idx_team_user` (`team_id`, `user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='团队成员表';

-- 系统配置表
CREATE TABLE `system_configs` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '配置ID',
    `key` VARCHAR(50) NOT NULL COMMENT '配置键',
    `value` TEXT NOT NULL COMMENT '配置值',
    `description` VARCHAR(200) DEFAULT NULL COMMENT '配置说明',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `idx_key` (`key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统配置表';

-- 存款账户表
CREATE TABLE `deposit_accounts` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '账户ID',
    `user_id` BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
    `type` VARCHAR(20) NOT NULL COMMENT '存款类型(活期/定期)',
    `amount` DECIMAL(20,2) DEFAULT 0.00 COMMENT '存款金额',
    `interest_rate` DECIMAL(5,2) NOT NULL COMMENT '年利率(%)',
    `start_date` DATE NOT NULL COMMENT '起始日期',
    `end_date` DATE DEFAULT NULL COMMENT '到期日期',
    `status` TINYINT DEFAULT 1 COMMENT '状态(1:正常,2:已提前支取)',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    KEY `idx_user` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='存款账户表';

-- 贷款账户表
CREATE TABLE `loan_accounts` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '账户ID',
    `user_id` BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
    `amount` DECIMAL(20,2) NOT NULL COMMENT '贷款金额',
    `interest_rate` DECIMAL(5,2) NOT NULL COMMENT '年利率(%)',
    `term` INT NOT NULL COMMENT '贷款期限(月)',
    `monthly_payment` DECIMAL(20,2) NOT NULL COMMENT '月供',
    `remaining_amount` DECIMAL(20,2) NOT NULL COMMENT '剩余本金',
    `start_date` DATE NOT NULL COMMENT '起始日期',
    `end_date` DATE NOT NULL COMMENT '到期日期',
    `status` TINYINT DEFAULT 1 COMMENT '状态(1:审核中,2:已放款,3:已还清,4:已拒绝)',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    KEY `idx_user` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='贷款账户表'; 