def test_register_creates_account_and_returns_token(client):
    response = client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "testpass123",
        "tenant_name": "Test Company",
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_register_duplicate_email_fails(client):
    client.post("/auth/register", json={
        "email": "dup@example.com",
        "password": "testpass123",
        "tenant_name": "Company A",
    })
    response = client.post("/auth/register", json={
        "email": "dup@example.com",
        "password": "anotherpass",
        "tenant_name": "Company B",
    })
    assert response.status_code == 400


def test_login_with_correct_credentials_succeeds(client):
    client.post("/auth/register", json={
        "email": "login@example.com",
        "password": "correctpass",
        "tenant_name": "Test Co",
    })
    response = client.post("/auth/login", json={
        "email": "login@example.com",
        "password": "correctpass",
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_with_wrong_password_fails(client):
    client.post("/auth/register", json={
        "email": "wrongpass@example.com",
        "password": "correctpass",
        "tenant_name": "Test Co",
    })
    response = client.post("/auth/login", json={
        "email": "wrongpass@example.com",
        "password": "wrongpass",
    })
    assert response.status_code == 401


def test_protected_endpoint_rejects_missing_token(client):
    response = client.post("/ask", json={"question": "hello"})
    assert response.status_code == 401
    