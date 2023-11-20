CREATE TABLE
    IS601_Brokers (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        rarity INT NOT NULL,
        life INT,
        power INT,
        defense INT,
        stonks INT,
        created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        check(
            rarity >= 1
            AND rarity <= 10
        ),
        check(life >= 0),
        check(power >= 0),
        check(defense >= 0),
        check(stonks >= 0)
    );