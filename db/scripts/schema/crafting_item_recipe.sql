CREATE TABLE crafting_item_recipe
(
    crafting_id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_made   TEXT    NOT NULL,
    recipe_id   INTEGER NOT NULL,
--     TODO: enforce item made and recipe id unique constraint
    FOREIGN KEY (crafting_id) REFERENCES block_obtaining_method (generates),
    FOREIGN KEY (item_made) REFERENCES items_and_groups (name),
    FOREIGN KEY (recipe_id) REFERENCES crafting_recipe (recipe_id)
);
