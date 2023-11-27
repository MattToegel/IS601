CREATE TABLE
    IS601_Point_History (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id int NOT NULL,
        points_change int NOT NULL,
        expected_total int NOT NULL,
        created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES IS601_Users(id),
        check (points_change != 0),
        check (expected_total >= 0)
    );