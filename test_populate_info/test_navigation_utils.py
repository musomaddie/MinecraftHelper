from unittest.mock import patch

from flask import session

import populate_info.resources as r
from conftest import ITEM_1, ITEM_2
from populate_info.navigation_utils import either_move_next_category_or_repeat, move_next_category

url_for_patch_str = "populate_info.navigation_utils.url_for"
redirect_patch_str = "populate_info.navigation_utils.redirect"


class TestMoveNextCategory:

    @patch(url_for_patch_str)
    @patch(redirect_patch_str)
    def test_all_items(self, mock_redirect, mock_url_for, request_context):
        session[r.SK_METHOD_LIST] = ["breaking", "crafting"]
        result = move_next_category(ITEM_1)
        mock_url_for.assert_called_once_with("breaking", item_name=ITEM_1)
        assert len(session[r.SK_METHOD_LIST]) == 1
        assert "crafting" in session[r.SK_METHOD_LIST]

        mock_url_for.reset_mock()
        result = move_next_category(ITEM_1)
        mock_url_for.assert_called_once_with("crafting", item_name=ITEM_1)
        assert len(session[r.SK_METHOD_LIST]) == 0

    @patch(url_for_patch_str)
    @patch(redirect_patch_str)
    def test_breaking_left(self, mock_redirect, mock_url_for, request_context):
        session[r.SK_METHOD_LIST] = ["breaking"]
        result = move_next_category(ITEM_1)
        mock_url_for.assert_called_once_with("breaking", item_name=ITEM_1)
        assert len(session[r.SK_METHOD_LIST]) == 0

    @patch(url_for_patch_str)
    @patch(redirect_patch_str)
    def test_none_left(self, mock_redirect, mock_url_for, request_context):
        session[r.SK_METHOD_LIST] = []
        result = move_next_category(ITEM_1)
        mock_url_for.assert_called_once_with("add.start_adding_item", item_name=ITEM_2)


class TestEitherMoveNextCategoryOrRepeat:

    @patch(url_for_patch_str)
    @patch(redirect_patch_str)
    def test_move_next(self, mock_redirect, mock_url_for, client, request_context):
        session[r.SK_METHOD_LIST] = ["next.method"]
        either_move_next_category_or_repeat(ITEM_1, "current.cat", {"next": "here"})
        mock_url_for.assert_called_once_with("next.method", item_name=ITEM_1)

    @patch(url_for_patch_str)
    @patch(redirect_patch_str)
    def test_repeat(self, mock_redirect, mock_url_for):
        either_move_next_category_or_repeat(ITEM_1, "current.cat", {"another": "here"})
        mock_url_for.assert_called_once_with("current.cat", item_name=ITEM_1)
