CREATE TABLE
    IS601_BrokerStocks (
        id INT AUTO_INCREMENT PRIMARY KEY,
        broker_id INT,
        symbol VARCHAR(10) NOT NULL,
        shares INT DEFAULT 1,
        FOREIGN KEY (broker_id) REFERENCES IS601_Brokers(id),
        FOREIGN KEY (symbol) REFERENCES IS601_Stocks(symbol),
        created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        UNIQUE (broker_id, symbol),
        -- enforces UNIQUE pairs
        check(shares > 0)
    );