CREATE TABLE item_trading
(
    trading_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    item_name     TEXT NOT NULL,
    villager_type TEXT NOT NULL,
    emerald_price INT,
    other_price   TEXT,
    FOREIGN KEY (trading_id) REFERENCES item_obtaining_method (generates),
    FOREIGN KEY (item_name) REFERENCES items_and_groups (name)
);
