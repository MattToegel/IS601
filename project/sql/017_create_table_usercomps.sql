CREATE TABLE
    IS601_S_UserComps(
        id int auto_increment PRIMARY KEY,
        comp_id int not null,
        user_id int not null,
        created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        modified TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        UNIQUE KEY (comp_id, user_id),
        FOREIGN KEY (comp_id) REFERENCES IS601_S_Comps(id),
        FOREIGN KEY (user_id) REFERENCES IS601_Users(id)
    )