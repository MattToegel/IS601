CREATE TABLE
    IS601_Stocks (
        id INT AUTO_INCREMENT PRIMARY KEY,
        symbol VARCHAR(10) NOT NULL,
        open DECIMAL(10, 4) NOT NULL,
        high DECIMAL(10, 4) NOT NULL,
        low DECIMAL(10, 4) NOT NULL,
        price DECIMAL(10, 4) NOT NULL,
        volume INT NOT NULL,
        latest_trading_day DATE NOT NULL,
        previous_close DECIMAL(10, 4) NOT NULL,
        -- reserved keywords must be wrapped in backticks
        `change` DECIMAL(10, 4) NOT NULL,
        change_percent DECIMAL(10, 4) NOT NULL,
        created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        UNIQUE KEY `symbol_latest_trading_day` (
            `symbol`,
            `latest_trading_day`
        )
    );