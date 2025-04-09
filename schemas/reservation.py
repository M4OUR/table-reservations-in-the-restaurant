from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ReservationCreate(BaseModel):
    customer_name: str
    table_id: int
    reservation_time: datetime
    duration_minutes: int
    end_time: Optional[datetime]

class ReservationOut(ReservationCreate):
    id: int

    class Config:
        orm_mode = True
