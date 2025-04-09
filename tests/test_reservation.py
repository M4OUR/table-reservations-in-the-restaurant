import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_table():
    response = client.post("/tables/", json={
        "name": "Table 42",
        "seats": 4,
        "location": "window"
    })
    assert response.status_code == 200
    assert response.json()["name"] == "Table 42"

def test_create_reservation():
    # Сначала создаём столик
    table_resp = client.post("/tables/", json={
        "name": "Test Table",
        "seats": 2,
        "location": "terrace"
    })
    table_id = table_resp.json()["id"]

    # Потом бронь на него
    res = client.post("/reservations/", json={
        "customer_name": "Alice",
        "table_id": table_id,
        "reservation_time": "2025-04-08T19:00:00",
        "duration_minutes": 60
    })
    assert res.status_code == 200
    assert res.json()["customer_name"] == "Alice"
