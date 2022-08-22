CREATE TABLE item_fishing
(
    fishing_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    item_name     TEXT NOT NULL,
    treasure_type TEXT NOT NULL,
    FOREIGN KEY (item_name) REFERENCES items_and_groups (item_name)
);
