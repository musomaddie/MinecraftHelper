CREATE TABLE item_trading
(
    trading_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    item_name      TEXT NOT NULL,
    villager_type  TEXT NOT NULL,
    villager_level TEXT,
    emerald_price  INT  NOT NULL,
    other_price    TEXT,
    FOREIGN KEY (trading_id) REFERENCES item_obtaining_method (generates),
    FOREIGN KEY (item_name) REFERENCES item_to_group (item_name)
);
