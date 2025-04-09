from pydantic import BaseModel

class TableCreate(BaseModel):
    name: str
    seats: int
    location: str

class TableOut(TableCreate):
    id: int

    class Config:
        orm_mode = True
