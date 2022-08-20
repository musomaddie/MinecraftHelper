CREATE TABLE item_breaking
(
    breaking_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    requires_tool       BOOLEAN NOT NULL,
    requires_silk_touch BOOLEAN NOT NULL,
    fastest_tool        TEXT,
    FOREIGN KEY (breaking_id) REFERENCES block_obtaining_method (generates),
    FOREIGN KEY (fastest_tool) REFERENCES items_and_groups (name)
);
