from collections import defaultdict
from typing import DefaultDict

import bs4
import requests
from bs4 import BeautifulSoup
import sqlite3

URL_ALL_BLOCKS_PAGE = " https://minecraft.fandom.com/wiki/Block#List_of_blocks"
URL_ALL_ITEMS_PAGE = "https://minecraft.fandom.com/wiki/Item"
DB_NAME = "block_list"


def init_block_list_database():
    page = requests.get(URL_ALL_BLOCKS_PAGE)
    soup = BeautifulSoup(page.content, "html.parser")

    block_list_lis = soup.find_all("div", class_="collapsible-content")[0].contents[0].find_all("li")
    item_names = [li_item.text.strip() for li_item in block_list_lis]

    # Set up and write to the database
    conn = sqlite3.connect(f"db/{DB_NAME}.db")
    cur = conn.cursor()
    cur.execute(f"DROP TABLE IF EXISTS {DB_NAME}")
    cur.execute(f"""CREATE TABLE {DB_NAME}
        (block_name TEXT PRIMARY KEY, block_group TEXT); """)
    calculated_groups = []
    for name in item_names:
        group = input(f"What block group does {name} belong to? ")
        calculated_groups.append(group)
        cur.execute(f'INSERT INTO {DB_NAME} VALUES ("{name}", "{group}");')
    print(calculated_groups)
    conn.commit()
    cur.close()
    conn.close()

def add_items_to_block_list():
    page = requests.get()


def sanity_check_group():
    conn = sqlite3.connect(f"db/{DB_NAME}.db")
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {DB_NAME}")
    result = cur.fetchall()
    # Make a dictionary
    group_dict = defaultdict(int)
    for r in result:
        group_dict[r[1]] += 1

    for key in sorted(list(group_dict.keys())):
        print(f"{key}: {group_dict[key]}")



if __name__ == '__main__':
    sanity_check_group()
