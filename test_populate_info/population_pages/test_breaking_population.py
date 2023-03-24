import populate_info.resources as r


def test_breaking_get(client):
    with client.session_transaction() as session_before:
        session_before[r.GROUP_NAME_SK] = "group name"
    response = client.get("/breaking/Testsing Item")
    assert response.status_code == 200
