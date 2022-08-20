CREATE TABLE crafting_item_recipe
(
    item_made TEXT,
    recipe_id INTEGER,
    PRIMARY KEY (item_made, recipe_id),
    FOREIGN KEY (item_made) REFERENCES items_and_groups (name),
    FOREIGN KEY (recipe_id) REFERENCES crafting_recipe (recipe_id)
);
