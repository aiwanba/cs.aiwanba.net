-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- 主机： 127.0.0.1
-- 生成日期： 2025-02-09 05:52:49
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
-- 表的结构 `chat_history`
--

CREATE TABLE `chat_history` (
  `id` bigint(20) NOT NULL,
  `session_id` varchar(64) NOT NULL COMMENT '会话ID',
  `role` varchar(20) NOT NULL COMMENT '发送者角色(user/assistant/system)',
  `content` text NOT NULL COMMENT '消息内容',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp() COMMENT '创建时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='聊天历史记录';

--
-- 转存表中的数据 `chat_history`
--

INSERT INTO `chat_history` (`id`, `session_id`, `role`, `content`, `created_at`) VALUES
(3, '6b8a9041-30da-4b49-8a4d-b84171ca22be', 'user', '你好啊，你是什么模型', '2025-02-09 04:44:43'),
(4, '6b8a9041-30da-4b49-8a4d-b84171ca22be', 'assistant', '<think>\n您好！我是由中国的深度求索（DeepSeek）公司开发的智能助手DeepSeek-R1。如您有任何任何问题，我会尽我所能为您提供帮助。\n</think>\n\n您好！我是由中国的深度求索（DeepSeek）公司开发的智能助手DeepSeek-R1。如您有任何任何问题，我会尽我所能为您提供帮助。', '2025-02-09 04:44:46'),
(5, '6b8a9041-30da-4b49-8a4d-b84171ca22be', 'user', '用的什么技术', '2025-02-09 04:45:14'),
(6, '6b8a9041-30da-4b49-8a4d-b84171ca22be', 'assistant', '<think>\n\n</think>\n\n我基于深度学习技术，具体来说是Transformer架构。通过大量文本数据的训练，我能够理解和生成自然语言。随着技术的迭代，我的性能也在不断优化。如果您对具体细节感兴趣，可以前往深度求索的官方网站（https://www.deepseek.com）查看更详细的信息。', '2025-02-09 04:45:17'),
(7, '6b8a9041-30da-4b49-8a4d-b84171ca22be', 'user', '你可以做什么', '2025-02-09 04:45:38'),
(8, '6b8a9041-30da-4b49-8a4d-b84171ca22be', 'assistant', '<think>\n\n</think>\n\n您好！我是由中国的深度求索（DeepSeek）公司开发的智能助手DeepSeek-R1。有关模型和产品的详细内容请参考官方文档。', '2025-02-09 04:45:40'),
(9, '6b8a9041-30da-4b49-8a4d-b84171ca22be', 'user', '您好！我是由中国的深度求索（DeepSeek）公司开发的智能助手DeepSeek-R1。有关模型和产品的详细内容请参考官方文档。', '2025-02-09 04:45:49'),
(10, '6b8a9041-30da-4b49-8a4d-b84171ca22be', 'assistant', '<think>\n\n</think>\n\n您好！我是由中国的深度求索（DeepSeek）公司开发的智能助手DeepSeek-R1。有关模型和产品的详细内容请参考官方文档。', '2025-02-09 04:45:51');

-- --------------------------------------------------------

--
-- 表的结构 `chat_sessions`
--

CREATE TABLE `chat_sessions` (
  `session_id` varchar(64) NOT NULL COMMENT '会话ID',
  `title` varchar(255) NOT NULL COMMENT '会话标题',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp() COMMENT '创建时间',
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp() COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='聊天会话';

--
-- 转存表中的数据 `chat_sessions`
--

INSERT INTO `chat_sessions` (`session_id`, `title`, `created_at`, `updated_at`) VALUES
('6b8a9041-30da-4b49-8a4d-b84171ca22be', '你好啊，你是什么模型...', '2025-02-09 04:44:43', '2025-02-09 04:45:51');

--
-- 转储表的索引
--

--
-- 表的索引 `chat_history`
--
ALTER TABLE `chat_history`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_session_id` (`session_id`);

--
-- 表的索引 `chat_sessions`
--
ALTER TABLE `chat_sessions`
  ADD PRIMARY KEY (`session_id`);

--
-- 在导出的表使用AUTO_INCREMENT
--

--
-- 使用表AUTO_INCREMENT `chat_history`
--
ALTER TABLE `chat_history`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
