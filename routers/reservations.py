from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from schemas.reservation import ReservationCreate, ReservationOut
from app.models import Reservation
from services.reservation_service import check_reservation_conflict
from typing import List
from datetime import timedelta

router = APIRouter(prefix="/reservations", tags=["Reservations"])


@router.get("/reservations/", response_model=List[ReservationOut])
def get_reservations(db: Session = Depends(get_db)):
    reservations = db.query(Reservation).all()  # Получаем все брони из базы
    return reservations


@router.post("/", response_model=ReservationOut)
def create_reservation(res: ReservationCreate, db: Session = Depends(get_db)):
    # Проверка на допустимую длительность брони (например, не менее 1 минуты и не более 24 часов)
    if res.duration_minutes <= 0 or res.duration_minutes > 1440:
        raise HTTPException(status_code=400, detail="Длительность брони должна быть в пределах от 1 до 1440 минут.")

    # Расчитываем время окончания брони
    end_time = res.reservation_time + timedelta(minutes=res.duration_minutes)

    # Проверяем на наличие конфликта брони с учётом времени начала и окончания
    if check_reservation_conflict(db, res, end_time):
        raise HTTPException(status_code=400, detail="Время уже занято для этого столика.")

    # Создаём новую бронь с учётом времени окончания
    reservation = Reservation(
        table_id=res.table_id,
        reservation_time=res.reservation_time,
        duration_minutes=res.duration_minutes,
        end_time=end_time
    )

    # Добавляем и сохраняем в базе данных
    db.add(reservation)
    db.commit()
    db.refresh(reservation)

    return reservation

@router.delete("/reservations/{reservation_id}")
def delete_reservation(reservation_id: int, db: Session = Depends(get_db)):
    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if reservation:
        db.delete(reservation)
        db.commit()
        return {"message": f"Reservation {reservation_id} has been deleted."}
    else:
        return {"error": "Reservation not found"}