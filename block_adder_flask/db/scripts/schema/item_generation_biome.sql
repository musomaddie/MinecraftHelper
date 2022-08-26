CREATE TABLE item_generation_biome
(
    generation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_name     TEXT NOT NULL,
    biome_name    TEXT NOT NULL,
    FOREIGN KEY (generation_id) REFERENCES item_obtaining_method (generates),
    FOREIGN KEY (item_name) REFERENCES item_to_group (item_name)
);
