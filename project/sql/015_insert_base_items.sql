INSERT INTO
    IS601_S_Items (
        id,
        name,
        description,
        stock,
        cost,
        image
    )
VALUES (
        -1,
        "Health Boost",
        "Live longer",
        9999999,
        10,
        ""
    ), (
        -2,
        "Agility",
        "Become the flash",
        9999999,
        15,
        ""
    ), (
        -3,
        "Quick Shot",
        "More pew pew",
        9999999,
        5,
        ""
    ), (
        -4,
        "Large Caliber",
        "One shot wonder",
        9999999,
        20,
        ""
    ), (
        -5,
        "Vaccuum",
        "Channel your inner Kirby",
        9999999,
        1,
        ""
    ) ON DUPLICATE KEY
UPDATE
    modified = CURRENT_TIMESTAMP()