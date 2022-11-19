CREATE TABLE
    IS601_Roles(
        id int auto_increment PRIMARY KEY,
        name VARCHAR(20) not null UNIQUE,
        description text not null,
        is_active tinyint(1) default 1,
        created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        modified TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    )