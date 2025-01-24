/* [数据库变更] 初始化用户表 - 李四 2024-03-20 */
CREATE TABLE users (
    id INT PRIMARY KEY,
    username VARCHAR(50) UNIQUE,
    password_hash VARCHAR(100) -- 修复d4e5f6g: 增加哈希字段
); 