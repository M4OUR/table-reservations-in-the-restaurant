from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import Table
from schemas.table import TableCreate, TableOut

router = APIRouter(prefix="/tables", tags=["Tables"])

@router.get("/", response_model=list[TableOut])
def get_all_tables(db: Session = Depends(get_db)):
    return db.query(Table).all()

@router.post("/", response_model=TableOut)
def create_table(table: TableCreate, db: Session = Depends(get_db)):
    new_table = Table(**table.dict())
    db.add(new_table)
    db.commit()
    db.refresh(new_table)
    return new_table

@router.delete("/{table_id}")
def delete_table(table_id: int, db: Session = Depends(get_db)):
    table = db.query(Table).filter(Table.id == table_id).first()
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    db.delete(table)
    db.commit()
    return {"detail": "Table deleted"}
