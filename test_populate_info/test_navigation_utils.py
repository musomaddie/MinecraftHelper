from unittest.mock import patch

from conftest import ITEM_1
from populate_info.navigation_utils import move_next_category, either_move_next_category_or_repeat

url_for_patch_str = "populate_info.navigation_utils.url_for"
redirect_patch_str = "populate_info.navigation_utils.redirect"


@patch(url_for_patch_str)
@patch(redirect_patch_str)
def test_move_next_category_breaking_left(mock_redirect, mock_url_for):
    category_list = ["breaking"]
    result = move_next_category(ITEM_1, category_list)
    mock_url_for.assert_called_once_with("breaking", item_name=ITEM_1)
    assert len(category_list) == 0


@patch(url_for_patch_str)
@patch(redirect_patch_str)
def test_move_next_category_none_left(mock_redirect, mock_url_for):
    result = move_next_category(ITEM_1, [])
    mock_url_for.assert_called_once_with("add.start_adding_item", item_name=ITEM_1)


@patch(url_for_patch_str)
@patch(redirect_patch_str)
def test_either_move_next_category_or_repeat_move_next(mock_redirect, mock_url_for):
    either_move_next_category_or_repeat(ITEM_1, "current.cat", ["next.method"], {"next": "here"})
    mock_url_for.assert_called_once_with("next.method", item_name=ITEM_1)


@patch(url_for_patch_str)
@patch(redirect_patch_str)
def test_either_move_next_category_or_repeat_repeat(mock_redirect, mock_url_for):
    either_move_next_category_or_repeat(ITEM_1, "current.cat", ["next.method"], {"another": "here"})
    mock_url_for.assert_called_once_with("current.cat", item_name=ITEM_1)
