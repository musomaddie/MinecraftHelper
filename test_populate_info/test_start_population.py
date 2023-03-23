from flask import session

import populate_info.resources as r
from conftest import GROUP_1, ITEM_1


def test_start_adding_item_get(client):
    response = client.get("/add_item/Testing Item")
    assert response.status_code == 200
    assert b"Testing" in response.data
    assert b"https://minecraft.fandom.com/wiki/Testing%20Item" in response.data


def test_start_adding_item_post_group_name(client):
    with client.session_transaction() as session_before:
        session_before[r.GROUP_NAME_SK] = "Old Group"
    with client:
        response = client.post(
            f"/add_item/{ITEM_1}", data={"group_name": GROUP_1, "group_name_btn": "Set group name"}
        )
        assert response.status_code == 302
        assert session[r.GROUP_NAME_SK] == GROUP_1


def test_start_redirects(client):
    assert client.get("/").status_code == 302
