import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from schemas.reservation import ReservationCreate, ReservationOut
from app.models import Reservation
from services.reservation_service import check_reservation_conflict
from typing import List
from datetime import timedelta

# Настройка логгирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reservations", tags=["Reservations"])

@router.get("/reservations/", response_model=List[ReservationOut])
def get_reservations(db: Session = Depends(get_db)):
    logger.info("Получение всех бронирований")  # Логируем действие
    reservations = db.query(Reservation).all()
    logger.info(f"Найдено {len(reservations)} бронирований.")  # Логируем количество найденных бронирований
    return [ReservationOut.from_orm(reservation) for reservation in reservations]

@router.post("/", response_model=ReservationOut)
def create_reservation(res: ReservationCreate, db: Session = Depends(get_db)):
    logger.info(f"Попытка создания бронирования для клиента: {res.customer_name}")  # Логируем создание бронирования

    # Проверка длительности бронирования
    if res.duration_minutes <= 0 or res.duration_minutes > 1440:
        logger.warning(f"Неверная длительность бронирования: {res.duration_minutes}")  # Логируем предупреждение
        raise HTTPException(status_code=400, detail="Длительность брони должна быть в пределах от 1 до 1440 минут.")

    # Рассчитываем время окончания
    end_time = res.reservation_time + timedelta(minutes=res.duration_minutes)

    # Проверяем наличие конфликта
    if check_reservation_conflict(db, res.table_id, res.reservation_time, end_time):
        logger.warning(f"Конфликт времени для столика {res.table_id}.")  # Логируем конфликт
        raise HTTPException(status_code=400, detail="Время уже занято для этого столика.")

    # Создание бронирования
    reservation = Reservation(
        customer_name=res.customer_name,
        table_id=res.table_id,
        reservation_time=res.reservation_time,
        duration_minutes=res.duration_minutes,
        end_time=end_time
    )

    db.add(reservation)
    db.commit()
    db.refresh(reservation)

    logger.info(f"Бронирование для {res.customer_name} успешно создано.")  # Логируем успешное создание
    return reservation

@router.delete("/reservations/{reservation_id}")
def delete_reservation(reservation_id: int, db: Session = Depends(get_db)):
    logger.info(f"Попытка удалить бронирование с ID {reservation_id}.")  # Логируем удаление
    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if reservation:
        db.delete(reservation)
        db.commit()
        logger.info(f"Бронирование {reservation_id} успешно удалено.")  # Логируем успешное удаление
        return {"message": f"Reservation {reservation_id} has been deleted."}
    else:
        logger.warning(f"Бронирование с ID {reservation_id} не найдено.")  # Логируем предупреждение
        raise HTTPException(status_code=404, detail="Reservation not found")
