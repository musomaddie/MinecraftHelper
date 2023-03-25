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
BREAKING_CAT_KEY = "breaking"
BREAKING_REQ_TOOL_KEY = "requires tool"
BREAKING_REQ_SPECIFIC_TOOL_KEY = "required tool"
BREAKING_FASTEST_TOOL_KEY = "fastest tool"
BREAKING_SILK_TOUCH_KEY = "silk touch"

# ############################## SESSION KEYS #############################################
CUR_ITEM_SK = "current_item"  # the item we are currently gathering information on.
GROUP_NAME_SK = "group"
USE_GROUP_VALUES_SK = "use_group_values"
METHOD_LIST_SK = "methods"


# ###################################### MISC ##############################################
def get_item_url(item_name: str) -> str:
    return f"https://minecraft.fandom.com/wiki/{item_name.replace(' ', '%20')}"


def clean_up_tool_name(tool_id: str) -> str:
    """ Taking in a tool name cleans it up ready for display. """
    tool_id.replace("_", " ").title()
    return tool_id


def idify_tool_name(tool_name: str) -> str:
    """ Inverse behaviour to clean_up_tool_name. """
    return tool_name.lower().replace(" ", "_")


# ####################################### JSON to HTML helpers ###########################################

def category_names_to_html_ids(category_names: list[str]) -> list[str]:
    helper_dict = {
        "breaking": "breaking_cbox"
    }
    return [helper_dict[cat_name] for cat_name in category_names if cat_name in helper_dict]
