CREATE TABLE
    IS601_MP2_Employees(
        id int auto_increment PRIMARY KEY,
        first_name VARCHAR (30),
        last_name VARCHAR(30),
        company_id int,
        email VARCHAR(60) UNIQUE,
        FOREIGN KEY (company_id) REFERENCES IS601_MP2_Companies(id),
        created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        modified TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    )