-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- 主机： 127.0.0.1
-- 生成日期： 2025-01-31 13:26:54
-- 服务器版本： 10.4.27-MariaDB
-- PHP 版本： 7.4.33

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- 数据库： `cs_aiwanba_net`
--

-- --------------------------------------------------------

--
-- 表的结构 `banks`
--

CREATE TABLE `banks` (
  `id` bigint(20) NOT NULL,
  `name` varchar(100) NOT NULL COMMENT '银行名称',
  `owner_id` bigint(20) NOT NULL COMMENT '所有者ID',
  `capital` decimal(20,2) NOT NULL COMMENT '注册资本',
  `reserve_ratio` decimal(5,2) DEFAULT 10.00 COMMENT '准备金率',
  `deposit_rate` decimal(5,2) NOT NULL COMMENT '存款利率',
  `loan_rate` decimal(5,2) NOT NULL COMMENT '贷款利率',
  `total_deposit` decimal(20,2) DEFAULT 0.00 COMMENT '存款总额',
  `total_loan` decimal(20,2) DEFAULT 0.00 COMMENT '贷款总额',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `status` tinyint(4) DEFAULT 1 COMMENT '状态：1-正常，0-破产'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='银行表';

--
-- 转存表中的数据 `banks`
--

INSERT INTO `banks` (`id`, `name`, `owner_id`, `capital`, `reserve_ratio`, `deposit_rate`, `loan_rate`, `total_deposit`, `total_loan`, `created_at`, `updated_at`, `status`) VALUES
(1, '测试银行1', 1, '50000000.00', '10.00', '3.80', '5.20', '50000000.00', '20000000.00', '2025-01-31 04:25:00', '2025-01-31 04:25:55', 1);

-- --------------------------------------------------------

--
-- 表的结构 `companies`
--

CREATE TABLE `companies` (
  `id` bigint(20) NOT NULL,
  `name` varchar(100) NOT NULL COMMENT '公司名称',
  `stock_code` varchar(6) NOT NULL COMMENT '股票代码',
  `industry` varchar(50) NOT NULL COMMENT '行业分类',
  `total_shares` bigint(20) NOT NULL COMMENT '总股本',
  `circulating_shares` bigint(20) NOT NULL COMMENT '流通股本',
  `initial_price` decimal(10,2) NOT NULL COMMENT '发行价',
  `current_price` decimal(10,2) NOT NULL COMMENT '当前股价',
  `cash_balance` decimal(20,2) NOT NULL COMMENT '公司现金',
  `founder_id` bigint(20) NOT NULL COMMENT '创始人ID',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `status` tinyint(4) DEFAULT 1 COMMENT '状态：1-正常，2-停牌，0-破产'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='公司表';

--
-- 转存表中的数据 `companies`
--

INSERT INTO `companies` (`id`, `name`, `stock_code`, `industry`, `total_shares`, `circulating_shares`, `initial_price`, `current_price`, `cash_balance`, `founder_id`, `created_at`, `updated_at`, `status`) VALUES
(1, '测试公司-更新', 'TS0001', '互联网', 100000, 100000, '10.00', '13.00', '1000000.00', 1, '2025-01-31 04:24:44', '2025-01-31 12:26:02', 1);

-- --------------------------------------------------------

--
-- 表的结构 `deposits`
--

CREATE TABLE `deposits` (
  `id` bigint(20) NOT NULL,
  `bank_id` bigint(20) NOT NULL COMMENT '银行ID',
  `user_id` bigint(20) NOT NULL COMMENT '用户ID',
  `amount` decimal(20,2) NOT NULL COMMENT '存款金额',
  `interest_rate` decimal(5,2) NOT NULL COMMENT '利率',
  `term` int(11) NOT NULL COMMENT '期限(天)',
  `start_date` timestamp NOT NULL DEFAULT current_timestamp() COMMENT '开始日期',
  `end_date` timestamp NULL DEFAULT NULL COMMENT '到期日期',
  `status` tinyint(4) DEFAULT 1 COMMENT '状态：1-正常，2-已支取，0-违约',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='存款表';

--
-- 转存表中的数据 `deposits`
--

INSERT INTO `deposits` (`id`, `bank_id`, `user_id`, `amount`, `interest_rate`, `term`, `start_date`, `end_date`, `status`, `created_at`, `updated_at`) VALUES
(1, 1, 1, '10000000.00', '3.50', 30, '2025-01-31 04:25:08', '2025-03-02 04:25:08', 1, '2025-01-31 04:25:08', '2025-01-31 04:25:08'),
(2, 1, 1, '10000000.00', '3.50', 30, '2025-01-31 04:25:09', '2025-03-02 04:25:09', 1, '2025-01-31 04:25:09', '2025-01-31 04:25:09'),
(3, 1, 1, '10000000.00', '3.50', 30, '2025-01-31 04:25:14', '2025-03-02 04:25:14', 1, '2025-01-31 04:25:14', '2025-01-31 04:25:14'),
(4, 1, 1, '10000000.00', '3.50', 30, '2025-01-31 04:25:43', '2025-03-02 04:25:43', 1, '2025-01-31 04:25:43', '2025-01-31 04:25:43'),
(5, 1, 1, '10000000.00', '3.50', 30, '2025-01-31 04:25:44', '2025-03-02 04:25:44', 1, '2025-01-31 04:25:44', '2025-01-31 04:25:44');

-- --------------------------------------------------------

--
-- 表的结构 `loans`
--

CREATE TABLE `loans` (
  `id` bigint(20) NOT NULL,
  `bank_id` bigint(20) NOT NULL COMMENT '银行ID',
  `user_id` bigint(20) NOT NULL COMMENT '借款人ID',
  `amount` decimal(20,2) NOT NULL COMMENT '贷款金额',
  `interest_rate` decimal(5,2) NOT NULL COMMENT '利率',
  `term` int(11) NOT NULL COMMENT '期限(天)',
  `start_date` timestamp NOT NULL DEFAULT current_timestamp() COMMENT '放款日期',
  `end_date` timestamp NULL DEFAULT NULL COMMENT '到期日期',
  `collateral_type` tinyint(4) DEFAULT NULL COMMENT '抵押品类型：1-股票，2-存单',
  `collateral_id` bigint(20) DEFAULT NULL COMMENT '抵押品ID',
  `status` tinyint(4) DEFAULT 1 COMMENT '状态：1-正常，2-已还清，0-违约',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='贷款表';

--
-- 转存表中的数据 `loans`
--

INSERT INTO `loans` (`id`, `bank_id`, `user_id`, `amount`, `interest_rate`, `term`, `start_date`, `end_date`, `collateral_type`, `collateral_id`, `status`, `created_at`, `updated_at`) VALUES
(1, 1, 1, '10000000.00', '4.90', 90, '2025-01-31 04:25:31', '2025-05-01 04:25:31', 1, 1, 1, '2025-01-31 04:25:31', '2025-01-31 04:25:31'),
(2, 1, 1, '10000000.00', '4.90', 90, '2025-01-31 04:25:32', '2025-05-01 04:25:32', 1, 1, 1, '2025-01-31 04:25:32', '2025-01-31 04:25:32');

-- --------------------------------------------------------

--
-- 表的结构 `messages`
--

CREATE TABLE `messages` (
  `id` bigint(20) NOT NULL,
  `type` tinyint(4) NOT NULL COMMENT '消息类型：1-系统公告，2-公司公告，3-交易提醒，4-风险预警',
  `title` varchar(200) NOT NULL COMMENT '标题',
  `content` text NOT NULL COMMENT '内容',
  `related_id` bigint(20) DEFAULT NULL COMMENT '关联ID',
  `priority` tinyint(4) DEFAULT 3 COMMENT '优先级：1-高，2-中，3-低',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `expire_at` timestamp NULL DEFAULT NULL COMMENT '过期时间',
  `status` tinyint(4) DEFAULT 1 COMMENT '状态：1-有效，0-已过期'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='消息表';

--
-- 转存表中的数据 `messages`
--

INSERT INTO `messages` (`id`, `type`, `title`, `content`, `related_id`, `priority`, `created_at`, `updated_at`, `expire_at`, `status`) VALUES
(1, 2, '新公司上市: 测试公司', '新公司测试公司(TS0001)已成功注册上市，总股本100000股，发行价10.0元', 1, 2, '2025-01-31 04:24:44', '2025-01-31 04:24:44', '2025-02-01 04:24:44', 1),
(2, 2, '公司信息更新: 测试公司-更新', '公司测试公司-更新(TS0001)信息已更新', 1, 2, '2025-01-31 04:24:52', '2025-01-31 04:24:52', '2025-02-01 04:24:52', 1),
(3, 2, '公司状态变更: 测试公司-更新', '公司测试公司-更新(TS0001)状态已变更为正常', 1, 1, '2025-01-31 04:24:57', '2025-01-31 04:24:57', '2025-02-01 04:24:57', 1),
(4, 1, '新银行开业: 测试银行1', '新银行测试银行1已开业，注册资本50000000.0元，存款利率3.5%，贷款利率4.9%，准备金率10.0%', NULL, 2, '2025-01-31 04:25:00', '2025-01-31 04:25:00', '2025-02-01 04:25:00', 1),
(5, 2, '银行利率变更: 测试银行1', '银行测试银行1利率已更新，存款利率3.8%，贷款利率5.2%', NULL, 2, '2025-01-31 04:25:55', '2025-01-31 04:25:55', '2025-02-01 04:25:55', 1),
(6, 1, '测试消息', '这是一条测试消息内容', NULL, 2, '2025-01-31 04:26:19', '2025-01-31 04:26:19', '2025-02-01 04:26:19', 1),
(7, 1, '系统广播消息', '这是一条广播消息', NULL, 1, '2025-01-31 04:26:21', '2025-01-31 04:26:21', '2025-02-01 04:26:21', 1);

-- --------------------------------------------------------

--
-- 表的结构 `message_recipients`
--

CREATE TABLE `message_recipients` (
  `id` bigint(20) NOT NULL,
  `message_id` bigint(20) NOT NULL COMMENT '消息ID',
  `user_id` bigint(20) NOT NULL COMMENT '接收用户ID',
  `is_read` tinyint(4) DEFAULT 0 COMMENT '是否已读：0-未读，1-已读',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='消息接收表';

--
-- 转存表中的数据 `message_recipients`
--

INSERT INTO `message_recipients` (`id`, `message_id`, `user_id`, `is_read`, `created_at`) VALUES
(1, 6, 1, 0, '2025-01-31 04:26:19'),
(2, 7, 1, 1, '2025-01-31 04:26:21');

-- --------------------------------------------------------

--
-- 表的结构 `orders`
--

CREATE TABLE `orders` (
  `id` bigint(20) NOT NULL,
  `company_id` bigint(20) NOT NULL COMMENT '公司ID',
  `user_id` bigint(20) NOT NULL COMMENT '用户ID',
  `order_type` tinyint(4) NOT NULL COMMENT '订单类型：1-买入，2-卖出',
  `price_type` tinyint(4) NOT NULL COMMENT '价格类型：1-市价，2-限价',
  `price` decimal(10,2) DEFAULT NULL COMMENT '委托价格',
  `quantity` bigint(20) NOT NULL COMMENT '委托数量',
  `filled_quantity` bigint(20) DEFAULT 0 COMMENT '已成交数量',
  `status` tinyint(4) DEFAULT 1 COMMENT '状态：1-未成交，2-部分成交，3-全部成交，4-已撤销',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='交易订单表';

--
-- 转存表中的数据 `orders`
--

INSERT INTO `orders` (`id`, `company_id`, `user_id`, `order_type`, `price_type`, `price`, `quantity`, `filled_quantity`, `status`, `created_at`, `updated_at`) VALUES
(1, 1, 1, 1, 2, '12.50', 10000, 0, 1, '2025-01-31 04:25:57', '2025-01-31 04:25:57'),
(2, 1, 1, 2, 2, '13.00', 10000, 10000, 3, '2025-01-31 04:26:00', '2025-01-31 04:26:02'),
(3, 1, 1, 1, 1, NULL, 10000, 10000, 3, '2025-01-31 04:26:02', '2025-01-31 04:26:02'),
(4, 1, 1, 1, 1, NULL, 10000, 0, 4, '2025-01-31 04:26:03', '2025-01-31 04:26:08');

-- --------------------------------------------------------

--
-- 表的结构 `shareholdings`
--

CREATE TABLE `shareholdings` (
  `id` bigint(20) NOT NULL,
  `company_id` bigint(20) NOT NULL COMMENT '公司ID',
  `user_id` bigint(20) NOT NULL COMMENT '股东ID',
  `shares` bigint(20) NOT NULL COMMENT '持股数量',
  `cost_price` decimal(10,2) NOT NULL COMMENT '成本价',
  `pledged_shares` bigint(20) DEFAULT 0 COMMENT '质押股份数',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='股权表';

--
-- 转存表中的数据 `shareholdings`
--

INSERT INTO `shareholdings` (`id`, `company_id`, `user_id`, `shares`, `cost_price`, `pledged_shares`, `created_at`, `updated_at`) VALUES
(1, 1, 1, 100000, '10.27', 0, '2025-01-31 04:24:44', '2025-01-31 04:26:02');

-- --------------------------------------------------------

--
-- 表的结构 `trades`
--

CREATE TABLE `trades` (
  `id` bigint(20) NOT NULL,
  `company_id` bigint(20) NOT NULL COMMENT '公司ID',
  `buy_order_id` bigint(20) NOT NULL COMMENT '买方订单ID',
  `sell_order_id` bigint(20) NOT NULL COMMENT '卖方订单ID',
  `price` decimal(10,2) NOT NULL COMMENT '成交价格',
  `quantity` bigint(20) NOT NULL COMMENT '成交数量',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='成交记录表';

--
-- 转存表中的数据 `trades`
--

INSERT INTO `trades` (`id`, `company_id`, `buy_order_id`, `sell_order_id`, `price`, `quantity`, `created_at`) VALUES
(1, 1, 3, 2, '13.00', 10000, '2025-01-31 04:26:02');

--
-- 触发器 `trades`
--
DELIMITER $$
CREATE TRIGGER `after_trade_insert` AFTER INSERT ON `trades` FOR EACH ROW BEGIN
            UPDATE companies 
            SET current_price = NEW.price,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = NEW.company_id;
        END
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- 表的结构 `transactions`
--

CREATE TABLE `transactions` (
  `id` bigint(20) NOT NULL,
  `user_id` bigint(20) NOT NULL COMMENT '用户ID',
  `type` tinyint(4) NOT NULL COMMENT '类型：1-创建公司，2-创建银行，3-存款，4-取款，5-贷款，6-还款',
  `amount` decimal(20,2) NOT NULL COMMENT '金额',
  `balance` decimal(20,2) NOT NULL COMMENT '变动后余额',
  `related_id` bigint(20) DEFAULT NULL COMMENT '关联ID',
  `description` varchar(200) DEFAULT NULL COMMENT '说明',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='资金流水表';

--
-- 转存表中的数据 `transactions`
--

INSERT INTO `transactions` (`id`, `user_id`, `type`, `amount`, `balance`, `related_id`, `description`, `created_at`, `updated_at`) VALUES
(1, 1, 1, '-1000000.00', '99000000.00', 1, '创建公司：测试公司', '2025-01-31 04:24:44', '2025-01-31 04:24:44'),
(2, 1, 2, '-50000000.00', '49000000.00', 1, '创建银行：测试银行1', '2025-01-31 04:25:00', '2025-01-31 04:25:00'),
(3, 1, 5, '10000000.00', '59000000.00', NULL, '贷款：10000000.0元，期限90天，利率4.90%', '2025-01-31 04:25:31', '2025-01-31 04:25:31'),
(4, 1, 5, '10000000.00', '69000000.00', NULL, '贷款：10000000.0元，期限90天，利率4.90%', '2025-01-31 04:25:32', '2025-01-31 04:25:32');

-- --------------------------------------------------------

--
-- 表的结构 `users`
--

CREATE TABLE `users` (
  `id` bigint(20) NOT NULL,
  `username` varchar(50) NOT NULL COMMENT '用户名',
  `password_hash` varchar(255) NOT NULL COMMENT '密码哈希',
  `email` varchar(100) NOT NULL COMMENT '邮箱',
  `cash` decimal(20,2) DEFAULT 10000000.00 COMMENT '现金余额',
  `is_admin` tinyint(4) DEFAULT 0 COMMENT '是否管理员：0-否，1-是',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `status` tinyint(4) DEFAULT 1 COMMENT '状态：1-正常，0-禁用'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

--
-- 转存表中的数据 `users`
--

INSERT INTO `users` (`id`, `username`, `password_hash`, `email`, `cash`, `is_admin`, `created_at`, `updated_at`, `status`) VALUES
(1, 'admin', '$2b$12$OCuvDws3tWskbrCeAtwfkeXQRkaBGYoKo1Ch6bV9ZQzW3zBuKxI7a', 'admin@test.com', '69000000.00', 1, '2025-01-31 04:23:49', '2025-01-31 04:25:32', 1);

--
-- 转储表的索引
--

--
-- 表的索引 `banks`
--
ALTER TABLE `banks`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `name` (`name`),
  ADD KEY `owner_id` (`owner_id`);

--
-- 表的索引 `companies`
--
ALTER TABLE `companies`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `name` (`name`),
  ADD UNIQUE KEY `stock_code` (`stock_code`),
  ADD KEY `founder_id` (`founder_id`),
  ADD KEY `idx_companies_stock_code` (`stock_code`);

--
-- 表的索引 `deposits`
--
ALTER TABLE `deposits`
  ADD PRIMARY KEY (`id`),
  ADD KEY `bank_id` (`bank_id`),
  ADD KEY `user_id` (`user_id`);

--
-- 表的索引 `loans`
--
ALTER TABLE `loans`
  ADD PRIMARY KEY (`id`),
  ADD KEY `bank_id` (`bank_id`),
  ADD KEY `user_id` (`user_id`);

--
-- 表的索引 `messages`
--
ALTER TABLE `messages`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_messages_type` (`type`);

--
-- 表的索引 `message_recipients`
--
ALTER TABLE `message_recipients`
  ADD PRIMARY KEY (`id`),
  ADD KEY `message_id` (`message_id`),
  ADD KEY `idx_message_recipients_user` (`user_id`);

--
-- 表的索引 `orders`
--
ALTER TABLE `orders`
  ADD PRIMARY KEY (`id`),
  ADD KEY `company_id` (`company_id`),
  ADD KEY `idx_orders_user` (`user_id`);

--
-- 表的索引 `shareholdings`
--
ALTER TABLE `shareholdings`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_holding` (`company_id`,`user_id`),
  ADD KEY `idx_shareholdings_user` (`user_id`);

--
-- 表的索引 `trades`
--
ALTER TABLE `trades`
  ADD PRIMARY KEY (`id`),
  ADD KEY `buy_order_id` (`buy_order_id`),
  ADD KEY `sell_order_id` (`sell_order_id`),
  ADD KEY `idx_trades_company` (`company_id`);

--
-- 表的索引 `transactions`
--
ALTER TABLE `transactions`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- 表的索引 `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`),
  ADD UNIQUE KEY `email` (`email`);

--
-- 在导出的表使用AUTO_INCREMENT
--

--
-- 使用表AUTO_INCREMENT `banks`
--
ALTER TABLE `banks`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- 使用表AUTO_INCREMENT `companies`
--
ALTER TABLE `companies`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- 使用表AUTO_INCREMENT `deposits`
--
ALTER TABLE `deposits`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- 使用表AUTO_INCREMENT `loans`
--
ALTER TABLE `loans`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- 使用表AUTO_INCREMENT `messages`
--
ALTER TABLE `messages`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- 使用表AUTO_INCREMENT `message_recipients`
--
ALTER TABLE `message_recipients`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- 使用表AUTO_INCREMENT `orders`
--
ALTER TABLE `orders`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- 使用表AUTO_INCREMENT `shareholdings`
--
ALTER TABLE `shareholdings`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- 使用表AUTO_INCREMENT `trades`
--
ALTER TABLE `trades`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- 使用表AUTO_INCREMENT `transactions`
--
ALTER TABLE `transactions`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- 使用表AUTO_INCREMENT `users`
--
ALTER TABLE `users`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- 限制导出的表
--

--
-- 限制表 `banks`
--
ALTER TABLE `banks`
  ADD CONSTRAINT `banks_ibfk_1` FOREIGN KEY (`owner_id`) REFERENCES `users` (`id`);

--
-- 限制表 `companies`
--
ALTER TABLE `companies`
  ADD CONSTRAINT `companies_ibfk_1` FOREIGN KEY (`founder_id`) REFERENCES `users` (`id`);

--
-- 限制表 `deposits`
--
ALTER TABLE `deposits`
  ADD CONSTRAINT `deposits_ibfk_1` FOREIGN KEY (`bank_id`) REFERENCES `banks` (`id`),
  ADD CONSTRAINT `deposits_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- 限制表 `loans`
--
ALTER TABLE `loans`
  ADD CONSTRAINT `loans_ibfk_1` FOREIGN KEY (`bank_id`) REFERENCES `banks` (`id`),
  ADD CONSTRAINT `loans_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- 限制表 `message_recipients`
--
ALTER TABLE `message_recipients`
  ADD CONSTRAINT `message_recipients_ibfk_1` FOREIGN KEY (`message_id`) REFERENCES `messages` (`id`),
  ADD CONSTRAINT `message_recipients_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- 限制表 `orders`
--
ALTER TABLE `orders`
  ADD CONSTRAINT `orders_ibfk_1` FOREIGN KEY (`company_id`) REFERENCES `companies` (`id`),
  ADD CONSTRAINT `orders_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- 限制表 `shareholdings`
--
ALTER TABLE `shareholdings`
  ADD CONSTRAINT `shareholdings_ibfk_1` FOREIGN KEY (`company_id`) REFERENCES `companies` (`id`),
  ADD CONSTRAINT `shareholdings_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- 限制表 `trades`
--
ALTER TABLE `trades`
  ADD CONSTRAINT `trades_ibfk_1` FOREIGN KEY (`company_id`) REFERENCES `companies` (`id`),
  ADD CONSTRAINT `trades_ibfk_2` FOREIGN KEY (`buy_order_id`) REFERENCES `orders` (`id`),
  ADD CONSTRAINT `trades_ibfk_3` FOREIGN KEY (`sell_order_id`) REFERENCES `orders` (`id`);

--
-- 限制表 `transactions`
--
ALTER TABLE `transactions`
  ADD CONSTRAINT `transactions_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
