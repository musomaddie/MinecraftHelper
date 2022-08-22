CREATE TABLE items_and_groups
(
    name          TEXT PRIMARY KEY,
    is_group      BOOLEAN NOT NULL,
    part_of_group BOOLEAN NOT NULL
);
-- TODO: clean this up so that the group names included here link well to what I should expect in links
