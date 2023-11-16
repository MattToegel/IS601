CREATE TABLE
    IS601_Stocks (
        id INT AUTO_INCREMENT PRIMARY KEY,
        Name VARCHAR(255) NOT NULL,
        Rarity INT NOT NULL,
        Life INT,
        Power INT,
        Defense INT,
        Stonks INT created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    );