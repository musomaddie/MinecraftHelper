DIR = "populate_info/item_data/"

# ######################################## FILE NAMES #################################################
ADDED_ITEM_FN = f"{DIR}added_items.json"
FULL_ITEMS_LIST_FN = f"{DIR}full_item_list.json"


def get_item_fn(item_name):
    return f"{DIR}{item_name}.json"


def get_group_fn(group_name: str):
    return f"{DIR}groups/{group_name.lower().replace(' ', '_')}.json"


# ########################################## JSON KEYS #########################################
ITEM_LIST_KEY = "items"
GROUP_NAME_KEY = "group name"
GROUP_ITEMS_KEY = "items"

# ############################## SESSION KEYS #############################################
CUR_ITEM_SK = "current_item"
GROUP_NAME_SK = "group"


# ###################################### MISC ##############################################
def get_item_url(item_name: str) -> str:
    return f"https://minecraft.fandom.com/wiki/{item_name.replace(' ', '%20')}"
