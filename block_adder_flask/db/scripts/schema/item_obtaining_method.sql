CREATE TABLE item_obtaining_method
(
    obtaining_id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_name    TEXT    NOT NULL,
    method       TEXT    NOT NULL,
    generates    INTEGER NOT NULL,
    FOREIGN KEY (item_name) REFERENCES item_to_group (item_name)
);
