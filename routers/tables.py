import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import Table
from schemas.table import TableCreate, TableOut

# Настройка логгирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tables", tags=["Tables"])


@router.get("/", response_model=list[TableOut])
def get_all_tables(db: Session = Depends(get_db)):
    logger.info("Получение всех таблиц")  # Логируем получение таблиц
    tables = db.query(Table).all()
    logger.info(f"Найдено {len(tables)} таблиц.")  # Логируем количество найденных таблиц
    return tables


@router.post("/", response_model=TableOut)
def create_table(table: TableCreate, db: Session = Depends(get_db)):
    # Проверка на существование таблицы с таким же названием и местоположением
    existing_table = db.query(Table).filter(Table.name == table.name, Table.location == table.location).first()
    if existing_table:
        raise HTTPException(status_code=400, detail="Таблица с таким названием и расположением уже существует.")

    new_table = Table(**table.dict())
    db.add(new_table)
    db.commit()
    db.refresh(new_table)
    return new_table



@router.delete("/{table_id}")
def delete_table(table_id: int, db: Session = Depends(get_db)):
    logger.info(f"Попытка удалить таблицу с ID {table_id}.")  # Логируем удаление таблицы
    table = db.query(Table).filter(Table.id == table_id).first()
    if not table:
        logger.warning(f"Таблица с ID {table_id} не найдена.")  # Логируем предупреждение, если таблица не найдена
        raise HTTPException(status_code=404, detail="Table not found")

    db.delete(table)
    db.commit()

    logger.info(f"Таблица с ID {table_id} успешно удалена.")  # Логируем успешное удаление
    return {"detail": "Table deleted"}
