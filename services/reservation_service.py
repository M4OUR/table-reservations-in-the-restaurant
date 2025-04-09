from sqlalchemy.orm import Session
from app.models import Reservation
from schemas.reservation import ReservationCreate
from datetime import datetime, timedelta

def check_reservation_conflict(db: Session, data: ReservationCreate, end_time: datetime):
    # Преобразуем все времена в наивные (без временной зоны)
    new_reservation_time = data.reservation_time.replace(tzinfo=None)
    new_end_time = end_time.replace(tzinfo=None)  # Используем переданный end_time

    # Получаем все существующие брони для выбранного стола
    existing_reservations = db.query(Reservation).filter(
        Reservation.table_id == data.table_id
    ).all()

    for reservation in existing_reservations:
        # Преобразуем время существующей брони в наивное
        existing_reservation_time = reservation.reservation_time.replace(tzinfo=None)
        existing_end_time = existing_reservation_time + timedelta(minutes=reservation.duration_minutes)

        # Сравниваем времена для пересечений
        if new_reservation_time < existing_end_time and existing_reservation_time < new_end_time:
            return True  # Есть пересечение

    return False  # Нет пересечений
