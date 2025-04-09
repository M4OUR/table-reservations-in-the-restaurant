import pytest
from fastapi.testclient import TestClient
from app.main import app  # Импортируем FastAPI приложение

client = TestClient(app)

# Тесты для создания столиков
def test_create_table():
    response = client.post("/tables/", json={"name": "Table 1", "seats": 4, "location": "Window area"})
    assert response.status_code == 200
    assert response.json()["name"] == "Table 1"
    assert response.json()["seats"] == 4
    assert response.json()["location"] == "Window area"

def test_get_tables():
    response = client.get("/tables/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_delete_table():
    # Сначала создаем столик
    response = client.post("/tables/", json={"name": "Table 2", "seats": 2, "location": "Terrace"})
    table_id = response.json()["id"]

    # Теперь удаляем его
    response = client.delete(f"/tables/{table_id}")
    assert response.status_code == 200
    assert response.json()["message"] == f"Table {table_id} has been deleted."


# Тесты для создания брони
def test_create_reservation():
    # Сначала создаем столик
    client.post("/tables/", json={"name": "Table 3", "seats": 2, "location": "Indoor"})

    # Теперь создаем бронь
    response = client.post("/reservations/", json={
        "customer_name": "John Doe",
        "table_id": 1,
        "reservation_time": "2025-04-08T18:00:00",  # Убедитесь, что время соответствует формату ISO 8601
        "duration_minutes": 60
    })

    assert response.status_code == 200
    assert response.json()["customer_name"] == "John Doe"
    assert response.json()["table_id"] == 1
    assert response.json()["reservation_time"] == "2025-04-08T18:00:00"
    assert response.json()["duration_minutes"] == 60

def test_get_reservations():
    response = client.get("/reservations/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_reservations():
    response = client.get("/reservations/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_reservation_conflict():
    # Сначала создаем столик
    client.post("/tables/", json={"name": "Table 4", "seats": 2, "location": "Patio"})

    # Создаем первую бронь
    response = client.post("/reservations/", json={
        "customer_name": "Jane Doe",
        "table_id": 2,
        "reservation_time": "2025-04-08T19:00:00",  # Время не пересекается
        "duration_minutes": 60
    })
    assert response.status_code == 200

    # Пытаемся создать конфликтную бронь
    response = client.post("/reservations/", json={
        "customer_name": "Michael Smith",
        "table_id": 2,
        "reservation_time": "2025-04-08T19:30:00",  # Время пересекается с предыдущей бронью
        "duration_minutes": 30
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "Время уже занято для этого столика."
