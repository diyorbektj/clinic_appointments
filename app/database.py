import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://diyorbek:root@localhost/clinic_db"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# app/crud.py
from sqlalchemy.orm import Session

from . import models, schemas


def get_appointment(db: Session, appointment_id: int):
    return (
        db.query(models.Appointment)
        .filter(models.Appointment.id == appointment_id)
        .first()
    )


def create_appointment(db: Session, appointment: schemas.AppointmentCreate):
    db_appointment = models.Appointment(**appointment.dict())
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment
