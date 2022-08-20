CREATE TABLE item_obtaining_method
(
    item_name TEXT    NOT NULL,
    method    TEXT    NOT NULL,
    generates INTEGER NOT NULL,
    PRIMARY KEY (item_name, method)
);
