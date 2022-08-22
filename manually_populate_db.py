import sqlite3

CRAFTING_TN = "crafting_item_recipe"
BREAKING_TN = "item_breaking"
FISHING_TN = "item_fishing"
NAT_GEN_BIOME_NAME = "item_generation_biome"
OBTAINING_TN = "item_obtaining_method"
TRADING_TN = "item_trading"
ITEMS_GROUPS_TN = "items_and_groups"
BLOCK_GROUP_TN = "block_to_group"

DB_NAME = "db/minecraft.db"
DB_S = "db/scripts/"


def connect_to_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    return conn, cur


def close_db(conn, cur):
    conn.commit()
    cur.close()
    conn.close()


def clear_database():
    conn, cur = connect_to_db()
    all_tables = [BREAKING_TN, FISHING_TN, NAT_GEN_BIOME_NAME, OBTAINING_TN, TRADING_TN]
    for table in all_tables:
        cur.execute(f'''DROP TABLE IF EXISTS {table}''')
        print(f"dropped table {table}")

    for table_name in all_tables:
        with open(f"db/schema/{table_name}.sql") as f:
            conn.executescript(f.read())
        print(f"added schema {table_name}")

    close_db(conn, cur)


def add_to_obtaining_table(conn, cur, block_name, method_name, id_title, table_name):
    cur.execute(
        f'''SELECT {id_title} FROM {table_name} WHERE item_name = "{block_name}"'''
    )
    ids = [row[0] for row in cur.fetchall()]
    with open(f"{DB_S}insert_{OBTAINING_TN}.sql") as f:
        for i in ids:
            conn.execute(f.read(), [block_name, method_name, i])


def add_trading(block, conn, cur):
    villager_types = []
    villager_levels = []
    emerald_prices = []
    others = []

    def _helper():
        villager_types.append(input("Villager? "))
        villager_levels.append(input("Villager skill level? "))
        emerald_prices.append(input("Emerald price? "))
        others.append(input("Other items (if required)? "))

    _helper()
    to_cont = input("add more? ")
    while to_cont == "y":
        _helper()
        to_cont = input("add more? ")

    # Insert
    for (vil, vil_l, em, o) in zip(villager_types, villager_levels, emerald_prices, others):
        with open(f"{DB_S}insert_{TRADING_TN}.sql") as f:
            conn.execute(f.read(), [block["name"], vil, vil_l, em, o])

    add_to_obtaining_table(conn, cur, block["name"], "trading", "trading_id", TRADING_TN)


def add_block(block, conn, cur):
    print(f"Adding information for {block}")
    if input(f"Can {block['name']} be obtained through trading? ") == "y":
        add_trading(block, conn, cur)


def add_manually():
    conn, cur = connect_to_db()
    cur.execute(f"SELECT * FROM {ITEMS_GROUPS_TN}")
    block_name_list = [{"name": r[0], "is_group": r[1] == "True", "part_of_group": r[2] == "True"}
                       for r in cur.fetchall()]
    cur.execute(f"SELECT item_name FROM {OBTAINING_TN}")
    already_calculated_blocks = [row[0] for row in cur.fetchall()]
    for block in block_name_list:
        if block["name"] in already_calculated_blocks:
            continue
        add_block(block, conn, cur)
        break


if __name__ == '__main__':
    print("starting")
    # clear_database()
    add_manually()
    print("finished")
