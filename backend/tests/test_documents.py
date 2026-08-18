import io


def _register_and_get_token(client, email="upload@example.com"):
    response = client.post("/auth/register", json={
        "email": email,
        "password": "testpass123",
        "tenant_name": "Upload Test Co",
    })
    return response.json()["access_token"]


def test_upload_requires_auth(client):
    file_content = b"col1,col2\nval1,val2\n"
    response = client.post(
        "/documents/upload",
        files={"file": ("test.csv", io.BytesIO(file_content), "text/csv")},
    )
    assert response.status_code == 401


def test_upload_rejects_unsupported_file_type(client):
    token = _register_and_get_token(client, "unsupported@example.com")
    response = client.post(
        "/documents/upload",
        files={"file": ("test.exe", io.BytesIO(b"not a real file"), "application/octet-stream")},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 400


def test_upload_csv_creates_document_with_ready_status(client):
    token = _register_and_get_token(client, "csvupload@example.com")
    csv_content = b"name,score\nAlice,90\nBob,85\n"
    response = client.post(
        "/documents/upload",
        files={"file": ("scores.csv", io.BytesIO(csv_content), "text/csv")},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["file_type"] == "csv"

    