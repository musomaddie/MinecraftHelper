DIR = "populate_info/item_data/"

# ######################################## FILE NAMES #################################################
ADDED_ITEM_FN = f"{DIR}added_items.json"
FULL_ITEMS_LIST_FN = f"{DIR}full_item_list.json"


def get_item_fn(item_name):
    return f"{DIR}{item_name}.json"


# ########################################## JSON KEYS #########################################
ITEM_LIST_KEY = "items"


# ###################################### MISC ##############################################
# URL_BLOCK_PAGE_TEMPLATE = "https://minecraft.fandom.com/wiki/"
def get_item_url(item_name: str) -> str:
    return f"https://minecraft.fandom.com/wiki/{item_name.replace(' ', '%20')}"
