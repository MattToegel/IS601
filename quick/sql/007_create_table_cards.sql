CREATE TABLE
    IS601_Quick_Cards (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) UNIQUE NOT NULL,
        text VARCHAR(300) NOT NULL,
        flavor_text TEXT,
        mana_cost TINYINT default 0,
        rarity VARCHAR(20) NOT NULL,
        card_class VARCHAR(15) NOT NULL,
        card_type VARCHAR(15) NOT NULL,
        card_set VARCHAR(100) NOT NULL default "No Set",
        spell_school VARCHAR(15) DEFAULT "",
        created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        check (mana_cost >= 0)
    );