CREATE TABLE item_breaking
(
    breaking_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    item_name           TEXT,
    requires_tool       BOOLEAN NOT NULL,
    requires_silk_touch BOOLEAN NOT NULL,
    fastest_tool        TEXT,
    FOREIGN KEY (breaking_id) REFERENCES item_obtaining_method (generates),
    FOREIGN KEY (item_name) REFERENCES items_and_groups (name),
    FOREIGN KEY (fastest_tool) REFERENCES items_and_groups (name)
);
