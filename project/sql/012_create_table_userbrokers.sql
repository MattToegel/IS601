CREATE TABLE
    IS601_UserBrokers(
        id int auto_increment PRIMARY KEY,
        broker_id int not null,
        user_id int not null,
        is_active tinyint(1) default 1,
        created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        modified TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES IS601_Users(id),
        FOREIGN KEY(broker_id) REFERENCES IS601_Brokers(id),
        UNIQUE KEY (user_id, broker_id)
    )