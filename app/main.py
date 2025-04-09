from fastapi import FastAPI
from app.db import Base, engine
from routers import tables, reservations

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Restaurant Booking API",
    version="1.0.0"
)

app.include_router(tables.router)
app.include_router(reservations.router)
