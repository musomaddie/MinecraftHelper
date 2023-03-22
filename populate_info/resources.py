DIR = "populate_info/item_data/"

# ######################################## FILE NAMES #################################################
ADDED_ITEM_FN = f"{DIR}added_items.json"
FULL_ITEMS_LIST_FN = f"{DIR}full_item_list.json"


def get_item_fn(item_name):
    return f"{DIR}{item_name}.json"


# ########################################## JSON KEYS #########################################
ITEM_LIST_KEY = "items"
