CREATE TABLE block_to_group
(
    block_name  TEXT PRIMARY KEY,
    block_group TEXT,
    FOREIGN KEY (block_name) REFERENCES items_and_groups (name),
    FOREIGN KEY (block_group) REFERENCES items_and_groups (name)
);
