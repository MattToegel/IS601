-- In my project I'll prefix the table with my project initial to avoid conflicts with future projects
CREATE TABLE
    IS601_S_Scores(
        id int auto_increment PRIMARY KEY,
        score int,
        hits int DEFAULT 0,
        defeated int DEFAULT 0,
        spawned int DEFAULT 0,
        ratio FLOAT DEFAULT 0,
        user_id int,
        FOREIGN KEY (user_id) REFERENCES IS601_Users(id),
        created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        modified TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    )