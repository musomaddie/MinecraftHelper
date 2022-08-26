CREATE TABLE item_natural_generation
(
    generation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_name     TEXT NOT NULL,
    structure     TEXT NOT NULL,
    container     TEXT,
    quantity      INT,
    chance        REAL,
    FOREIGN KEY (generation_id) REFERENCES item_obtaining_method (generates),
    FOREIGN KEY (item_name) REFERENCES item_to_group (item_name)

);
