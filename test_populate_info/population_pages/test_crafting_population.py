def test_crafting_get(client, session_with_group):
    response = client.get("/crafting/Testing Item")
    assert response.status_code == 200
