CREATE TABLE
    IS601_MP2_Companies(
        id int auto_increment PRIMARY KEY,
        name VARCHAR(60) unique,
        address VARCHAR(100),
        city VARCHAR(20),
        country VARCHAR(20),
        state VARCHAR(3),
        zip VARCHAR(5),
        website TEXT,
        created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        modified TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    )