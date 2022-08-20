import sqlite3
from sqlite3 import Row

import requests
from bs4 import BeautifulSoup

URL_BLOCK_PAGE_TEMPLATE = "https://minecraft.fandom.com/wiki/"
ITEM_GROUPS_TABLE_NAME = "items_and_groups"
BLOCK_TABLE_NAME = "block_to_group"
CRAFTING_TABLE_NAME = "crafting_item_recipe"
RECIPE_TABLE_NAME = "crafting_recipe"
OBTAINING_TABLE_NAME = "item_obtaining_method"
BREAKING_TABLE_NAME = "item_breaking"
TRADING_TABLE_NAME = "item_trading"
NAT_GEN_TABLE_NAME = "item_natural_generation"

DB_NAME = "db/minecraft.db"


def connect_to_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = Row
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


def _get_all_blocks(cur):
    cur.execute(f"SELECT * FROM {ITEM_GROUPS_TABLE_NAME}")
    return [
        {"name": r[0], "is_group": r[1] == "True", "part_of_group": r[2] == "True"}
        for r in cur.fetchall()]


def _get_current_recipes(cur):
    cur.execute(f"SELECT * FROM {CRAFTING_TABLE_NAME}")
    return [r[0] for r in cur.fetchall()]


def _get_blocks_to_groups(cur):
    cur.execute(f"SELECT * FROM {BLOCK_TABLE_NAME}")
    return {r[0]: r[1] for r in cur.fetchall()}


def init_schema():
    conn, cur = connect_to_db()
    tables = [
        CRAFTING_TABLE_NAME,
        RECIPE_TABLE_NAME,
        BREAKING_TABLE_NAME,
        OBTAINING_TABLE_NAME,
        TRADING_TABLE_NAME,
        NAT_GEN_TABLE_NAME
    ]
    for table in tables:
        cur.execute(f"DROP TABLE IF EXISTS {table}")

    for table in tables:
        _add_from_schema_file(conn, table)
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

    # NOTE: map or explorer map needs to be expanded out into two items.

    for item in full_list:
        cur.execute(
            f''' INSERT INTO {ITEM_GROUPS_TABLE_NAME} 
            VALUES ("{item}", "{item in groups}", "{item in part_of_group_item_list}");
        ''')

    close_db(conn, cur)


def repopulate_blocks_table():
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
    close_db(conn, cur)


def _get_all_paragraph_elements(starting_point, end_name):
    paragraphs = []
    current_item = starting_point.next_sibling
    while True:
        if current_item.name == end_name:
            return paragraphs
        if current_item.name == "p":
            paragraphs.append(current_item)
        current_item = current_item.next_sibling


def _find_table_type(starting_point, end_search_name):
    current_item = starting_point.next_sibling
    while True:
        if current_item.name == "table":
            return current_item
        if current_item.name == end_search_name:
            return
        current_item = current_item.next_sibling


def add_trading(block_name, conn, trading_heading_element):
    # TODO: not sure of a nice way to auto generate the trading information.
    all_paragraph_elements = _get_all_paragraph_elements(trading_heading_element, "h3")
    print(f"Please enter the trading information extracted from below {block_name}")
    print(all_paragraph_elements)
    villager_types = []
    emerald_price = []
    other_item = []
    while True:
        to_continue = input("Continue? (y) ")
        if to_continue != "y":
            break
        villager_types.append(input("Villager? "))
        emerald_price.append(input("Emerald price? "))
        other_item.append(input("Other items required? "))
    print()

    for villager, emerald, other in zip(villager_types, emerald_price, other_item):
        if other_item == "":
            with open("db/scripts/insert_item_trading_no_other_price.sql") as f:
                conn.execute(f.read(), [block_name, villager, emerald])
        else:
            with open("db/scripts/insert_item_trading.sql") as f:
                conn.execute(f.read(), [block_name, villager, emerald, other])


def add_natural_gen(block_name, conn, natural_gen_heading_element):
    table = _find_table_type(natural_gen_heading_element, "h3")
    rows = []
    current_structure = ""
    structures = []
    containers = []
    quantities = []
    chances = []
    seen_java = False
    seen_first_cell = False
    for desc in table.descendants:
        if desc.name == "tr":
            if "bedrock edition" in desc.text.strip().lower():
                break
            if not seen_java:
                if desc.text.strip().lower() == "java edition":
                    seen_java = True
                continue
            tds = desc.find_all("td")
            num_items = len(tds)
            # Must have at least 3 items
            chances.append(float(tds[-1].text.strip().replace("%", "")))
            quantities.append(int(tds[-2].text.strip()))
            containers.append(tds[-3].text.strip().replace("\xa0", " "))
            if num_items == 3:
                structures.append(current_structure)
            else:
                s = tds[-4].text.strip().replace("\xa0", " ")
                current_structure = s
                structures.append(s)

    for structure, container, quantity, chance in zip(structures, quantities, containers, chances):
        with open("db/scripts/insert_item_natural_generation.sql") as f:
            conn.execute(f.read(), [block_name, structure, container, quantity, chance])


def read_obtaining(block_name, conn, obtaining_heading_element):
    current_item = obtaining_heading_element.next_sibling
    while True:
        if current_item.name == "h2":
            break
        if current_item.name == "h3":
            text = current_item.text.strip().lower()
            if text == "trading[]":
                add_trading(block_name, conn, current_item)
            if text == "natural generation[]":
                add_natural_gen(block_name, conn, current_item)
        current_item = current_item.next_sibling


def add_recipes():
    conn, cur = connect_to_db()
    block_list = _get_all_blocks(cur)
    blocks_to_group = _get_blocks_to_groups(cur)
    current_recipes = []
    for block in block_list:
        if block["name"] in current_recipes:
            print(f"Skipping {block['name']} as already completed")
            continue
        print(f"Processing {block}")
        url_name = blocks_to_group[block["name"]] if block["part_of_group"] else block["name"]
        page = requests.get(f"{URL_BLOCK_PAGE_TEMPLATE}{url_name}")
        soup = BeautifulSoup(page.content, "html.parser")
        heading_element = soup.find(id="Obtaining").parent
        read_obtaining(url_name, conn, heading_element)
        conn.commit()
        current_recipes.append(block["name"])

        finish = input("Quit? (y) ")
        if finish == "y":
            break


if __name__ == '__main__':
    # repopulate_blocks_table()
    # make_groups_table()
    # init_schema()
    add_recipes()
