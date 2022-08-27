CREATE TABLE crafting_recipe
(
    recipe_id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    item_created               TEXT    NOT NULL,
    crafting_slot_1            TEXT,
    crafting_slot_2            TEXT,
    crafting_slot_3            TEXT,
    crafting_slot_4            TEXT,
    crafting_slot_5            TEXT,
    crafting_slot_6            TEXT,
    crafting_slot_7            TEXT,
    crafting_slot_8            TEXT,
    crafting_slot_9            TEXT,
    number_created             INT,
    works_four_by_four         BOOLEAN NOT NULL,
    requires_exact_positioning BOOLEAN NOT NULL,
    FOREIGN KEY (crafting_slot_1) REFERENCES item_to_group (item_name),
    FOREIGN KEY (crafting_slot_2) REFERENCES item_to_group (item_name),
    FOREIGN KEY (crafting_slot_3) REFERENCES item_to_group (item_name),
    FOREIGN KEY (crafting_slot_4) REFERENCES item_to_group (item_name),
    FOREIGN KEY (crafting_slot_5) REFERENCES item_to_group (item_name),
    FOREIGN KEY (crafting_slot_6) REFERENCES item_to_group (item_name),
    FOREIGN KEY (crafting_slot_7) REFERENCES item_to_group (item_name),
    FOREIGN KEY (crafting_slot_8) REFERENCES item_to_group (item_name),
    FOREIGN KEY (crafting_slot_9) REFERENCES item_to_group (item_name)
);

-- A null crafting slot represents that there is nothing there
-- For 9x9 recipes (works four by four is false) the slots are numbered as follows:
--     +-----------+
--     | 1 | 2 | 3 |
--     +-----------+
--     | 4 | 5 | 6 |
--     +-----------+
--     | 7 | 8 | 9 |
--     +-----------+

-- For 4x4 recipes the slots are numbered as:
--     +-------+
--     | 1 | 2 |
--     +-------+
--     | 3 | 4 |
--     +-------+


