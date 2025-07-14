from fastapi.testclient import TestClient
from first_task import main

client = TestClient(main)

def test_create_contact():
    response = client.post("/contacts", json={
        "name": "John",
        "email": "john@example.com",
        "phone": "1234567890"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "John"
