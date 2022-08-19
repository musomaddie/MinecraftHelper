from collections import defaultdict
from typing import DefaultDict

import bs4
import requests
from bs4 import BeautifulSoup
import sqlite3

URL_ALL_BLOCKS_PAGE = " https://minecraft.fandom.com/wiki/Block#List_of_blocks"
URL_ALL_ITEMS_PAGE = "https://minecraft.fandom.com/wiki/Item"
BLOCK_TABLE_NAME = "block_list"
DB_NAME = "db/minecraft.db"


def connect_to_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    return conn, cur


def close_db(conn, cur):
    conn.commit()
    cur.close()
    conn.close()


def init_block_list_database():
    page = requests.get(URL_ALL_BLOCKS_PAGE)
    soup = BeautifulSoup(page.content, "html.parser")

    block_list_lis = soup.find_all("div", class_="collapsible-content")[0].contents[0].find_all("li")
    item_names = [li_item.text.strip() for li_item in block_list_lis]

    # Set up and write to the database
    conn, cur = connect_to_db()
    cur.execute(f"DROP TABLE IF EXISTS {BLOCK_TABLE_NAME}")
    cur.execute(f"""CREATE TABLE {BLOCK_TABLE_NAME}
        (block_name TEXT PRIMARY KEY, block_group TEXT); """)
    calculated_groups = []
    for name in item_names:
        group = input(f"What block group does {name} belong to? ")
        calculated_groups.append(group)
        cur.execute(f'INSERT INTO {BLOCK_TABLE_NAME} VALUES ("{name}", "{group}");')
    close_db(conn, cur)


def add_items_to_block_list():
    page = requests.get(URL_ALL_ITEMS_PAGE)
    soup = BeautifulSoup(page.content, "html.parser")

    item_lists = soup.find_all("div", class_="div-col")
    # I only care about the first 3 from here
    item_names = []
    for i in range(3):
        item_list = item_lists[i].contents[1].find_all("li")
        item_names = item_names + [item.text.strip() for item in item_list]

    conn = sqlite3.connect(f"db/{BLOCK_TABLE_NAME}.db")
    cur = conn.cursor()
    conn, cur = connect_to_db()
    for name in item_names:
        try:
            cur.execute(f'INSERT INTO {BLOCK_TABLE_NAME} VALUES ("{name}", "");')
        except sqlite3.IntegrityError:
            continue
    close_db(conn, cur)


def sanity_check_group():
    conn, cur = connect_to_db()
    cur.execute(f"SELECT * FROM {BLOCK_TABLE_NAME}")
    result = cur.fetchall()
    # Make a dictionary
    group_dict = defaultdict(int)
    for r in result:
        group_dict[r[1]] += 1

    for key in sorted(list(group_dict.keys())):
        print(f"{key}: {group_dict[key]}")


def move_db():
    OLD_DB_NAME = "db/block_list.db"
    conn = sqlite3.connect(OLD_DB_NAME)
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {BLOCK_TABLE_NAME}")
    results = cur.fetchall()
    close_db(conn, cur)

    conn, cur = connect_to_db()
    cur.execute(f"DROP TABLE IF EXISTS {BLOCK_TABLE_NAME}")
    cur.execute(f"""CREATE TABLE {BLOCK_TABLE_NAME}
            (block_name TEXT PRIMARY KEY, block_group TEXT); """)
    for result in results:
        cur.execute(f'INSERT INTO {BLOCK_TABLE_NAME} VALUES ("{result[0]}", "{result[1]}");')
    close_db(conn, cur)


if __name__ == '__main__':
    move_db()
