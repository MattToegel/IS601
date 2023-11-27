ALTER TABLE IS601_Users
ADD
    COLUMN points int not null default 0 CHECK (points >= 0);