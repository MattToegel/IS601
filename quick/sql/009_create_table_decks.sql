CREATE TABLE
    IS601_Quick_WatchList (
        id INT AUTO_INCREMENT PRIMARY KEY,
        card_id int not null,
        user_id int not null,
        created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY(card_id) REFERENCES IS601_Quick_Cards(id),
        FOREIGN KEY(user_id) REFERENCES IS601_Users(id),
        UNIQUE KEY(card_id, user_id)
    );