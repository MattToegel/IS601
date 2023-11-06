CREATE TABLE
    IS601_MP3_Organizations(
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(60) UNIQUE,
        address VARCHAR(100),
        city VARCHAR(20),
        country VARCHAR(20),
        state VARCHAR(3),
        zip VARCHAR(5),
        website TEXT,
        description TEXT,
        created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        modified TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    );