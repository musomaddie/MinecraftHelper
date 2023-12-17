from flask import session

DIR = "populate_info/item_data/"

# ######################################## FILE NAMES #################################################
ADDED_ITEM_FN = f"{DIR}all_items/added_items.json"
FULL_ITEMS_LIST_FN = f"{DIR}all_items/full_item_list.json"


def get_item_fn(item_name):
    """ Returns the filename corresponding to the given item. """
    return f"{DIR}{item_name.replace(' ', '_').lower()}.json"


def get_group_fn(group_name: str):
    """ Returns the filename corresponding to the given group. """
    return f"{DIR}groups/{group_name.lower().replace(' ', '_')}.json"


# ########################################## JSON KEYS #########################################
KEY_GROUP_NAME = "group name"
KEY_ITEM_NAME = "item name"
KEY_ITEM_LIST = "items"
KEY_GROUP_ITEMS = "items"

# ############# Category keys
CK_BREAKING = "breaking"
CK_CRAFTING = "crafting"
CK_ENV_CHANGES = "environment changes"

# ############################## SESSION KEYS #############################################
SK_CUR_ITEM = "current_item"  # the item we are currently gathering information on.
SK_GROUP_NAME = "group"
SK_USE_GROUP_VALUES = "use_group_values"
SK_METHOD_LIST = "methods"


# ###################################### MISC ##############################################
def get_item_url(item_name: str) -> str:
    return f"https://minecraft.fandom.com/wiki/{item_name.replace(' ', '%20')}"


def clean_up_tool_name(tool_id: str) -> str:
    """ Taking in a tool name cleans it up ready for display. """
    tool_id.replace("-", " ")
    return tool_id.title()


def idify_tool_name(tool_name: str) -> str:
    """ Inverse behaviour to clean_up_tool_name. """
    return tool_name.lower().replace(" ", "-")


# ####################################### JSON to HTML helpers ###########################################

def category_names_to_html_ids(category_names: list[str]) -> list[str]:
    # Check if I actually need this.
    if not session.get(SK_USE_GROUP_VALUES, False):
        return []
    helper_dict = {
        "breaking": "breaking-cbox",
        "crafting": "crafting-cbox",
        "environment changes": "env-changes-cbox"
    }
    return [helper_dict[cat_name] for cat_name in category_names if cat_name in helper_dict]
