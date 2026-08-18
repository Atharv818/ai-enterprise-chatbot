def _register_and_get_token(client, email, tenant_name):
    response = client.post("/auth/register", json={
        "email": email,
        "password": "testpass123",
        "tenant_name": tenant_name,
    })
    return response.json()["access_token"]


def test_two_tenants_cannot_see_each_others_conversations(client):
    token_a = _register_and_get_token(client, "tenanta@example.com", "Tenant A")
    token_b = _register_and_get_token(client, "tenantb@example.com", "Tenant B")

    response_a = client.post(
        "/ask",
        json={"question": "hello"},
        headers={"Authorization": f"Bearer {token_a}"},
    )
    conversation_id = response_a.json()["conversation_id"]

    response_b = client.get(
        f"/conversations/{conversation_id}",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert response_b.status_code == 404  # not found, not leaked


def test_tenant_b_conversation_list_does_not_include_tenant_a(client):
    token_a = _register_and_get_token(client, "isoa@example.com", "Iso A")
    token_b = _register_and_get_token(client, "isob@example.com", "Iso B")

    client.post("/ask", json={"question": "hello"}, headers={"Authorization": f"Bearer {token_a}"})

    response_b = client.get("/conversations", headers={"Authorization": f"Bearer {token_b}"})
    assert response_b.status_code == 200
    assert response_b.json() == []  

