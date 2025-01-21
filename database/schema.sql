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
    stock_symbol VARCHAR(10) NOT NULL,
    quantity INT NOT NULL,
    price FLOAT NOT NULL,
    transaction_type ENUM('buy', 'sell') NOT NULL,
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES company(id)
); 