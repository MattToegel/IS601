CREATE TABLE
    IF NOT EXISTS IS601_S_Orders(
        id int AUTO_INCREMENT PRIMARY KEY,
        total_spent int,
        number_of_items int,
        user_id int,
        created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES IS601_Users(id)
    )