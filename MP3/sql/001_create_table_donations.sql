CREATE TABLE
    IS601_MP3_Donations(
        id INT AUTO_INCREMENT PRIMARY KEY,
        organization_id INT,
        donor_firstname VARCHAR(50),
        donor_lastname VARCHAR(50),
        donor_email VARCHAR(100),
        item_name VARCHAR(100),
        item_description TEXT,
        item_quantity INT,
        donation_date DATE,
        comments TEXT,
        created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        modified TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (organization_id) REFERENCES IS601_MP3_Organizations(id)
    );