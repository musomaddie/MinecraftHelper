import sqlite3

URL_BLOCK_PAGE_TEMPLATE = "https://minecraft.fandom.com/wiki/"
ITEM_GROUPS_TABLE_NAME = "items_and_groups"
BLOCK_TABLE_NAME = "block_to_group"
CRAFTING_TABLE_NAME = "crafting_item_recipe"
RECIPE_TABLE_NAME = "crafting_recipe"
DB_NAME = "db/minecraft.db"


def connect_to_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    return conn, cur


def close_db(conn, cur):
    conn.commit()
    cur.close()
    conn.close()


def _add_from_schema_file(conn, table_name):
    with open(f"db/schema/{table_name}.sql") as f:
        conn.executescript(f.read())
        print("added schema")


def init_schema():
    conn, cur = connect_to_db()
    cur.execute(f"DROP TABLE IF EXISTS {CRAFTING_TABLE_NAME}")
    cur.execute(f"DROP TABLE IF EXISTS {RECIPE_TABLE_NAME}")

    _add_from_schema_file(conn, RECIPE_TABLE_NAME)
    _add_from_schema_file(conn, CRAFTING_TABLE_NAME)

    close_db(conn, cur)


def make_groups_table():
    conn, cur = connect_to_db()
    cur.execute(f"DROP TABLE IF EXISTS {ITEM_GROUPS_TABLE_NAME}")
    print("dropped table")
    cur.execute(f"SELECT * FROM {BLOCK_TABLE_NAME}")
    og_items_with_groups = cur.fetchall()
    groups = set([item[1] for item in og_items_with_groups])
    print(og_items_with_groups)
    part_of_group_item_list = set(
        [item[0] for item in og_items_with_groups if item[1] is not None and item[1] != ""]
    )

    full_list = set(
        [item[0] for item in og_items_with_groups]
        + [item[1] for item in og_items_with_groups])

    _add_from_schema_file(conn, ITEM_GROUPS_TABLE_NAME)

    for item in full_list:
        cur.execute(
            f''' INSERT INTO {ITEM_GROUPS_TABLE_NAME} 
            VALUES ("{item}", "{item in groups}", "{item in part_of_group_item_list}");
        ''')

    close_db(conn, cur)


def repolulate_blocks_table():
    OLD_DB_NAME = "db/block_list.db"
    conn = sqlite3.connect(OLD_DB_NAME)
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM block_list")
    results = cur.fetchall()
    close_db(conn, cur)

    conn, cur = connect_to_db()
    cur.execute(f"DROP TABLE IF EXISTS {BLOCK_TABLE_NAME}")
    _add_from_schema_file(conn, BLOCK_TABLE_NAME)

    for result in results:
        if result[1] == "":
            cur.execute(
                f'INSERT INTO {BLOCK_TABLE_NAME} VALUES ("{result[0]}", null);')
        else:
            cur.execute(
                f'INSERT INTO {BLOCK_TABLE_NAME} VALUES ("{result[0]}", "{result[1]}");')
    print("insert blocks")
    close_db(conn, cur)


def add_recipes():
    conn, cur = connect_to_db()
    # page = requests.get(URL_ALL_BLOCKS_PAGE)
    # soup = BeautifulSoup(page.content, "html.parser")
    #
    # block_list_lis = soup.find_all("div", class_="collapsible-content")[0].contents[0].find_all(
    #     "li")
    # item_names = [li_item.text.strip() for li_item in block_list_lis]


if __name__ == '__main__':
    # make_groups_table()
    # repolulate_blocks_table()
    # init_schema()
    add_recipes()

    print()
    print("Nothing left to do")
