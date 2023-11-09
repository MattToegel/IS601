CREATE TABLE
    IS601_UserRoles(
        id int auto_increment PRIMARY KEY,
        role_id int not null,
        user_id int not null,
        is_active tinyint(1) default 1,
        created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        modified TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        UNIQUE KEY (role_id, user_id),
        FOREIGN KEY role_id REFERENCES IS601_Roles(id),
        FOREIGN KEY user_id REFERENCES IS601_Users(id)
    )
