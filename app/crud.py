from sqlalchemy.orm import Session

from . import models, schemas


# ----- Appointment CRUD -----
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


# ----- Doctor CRUD -----
def create_doctor(db: Session, doctor: schemas.DoctorCreate):
    db_doctor = models.Doctor(**doctor.dict())
    db.add(db_doctor)
    db.commit()
    db.refresh(db_doctor)
    return db_doctor


def get_doctor(db: Session, doctor_id: int):
    return db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()


def get_all_doctors(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Doctor).offset(skip).limit(limit).all()


def get_appointments_by_doctor(db: Session, doctor_id: int):
    return (
        db.query(models.Appointment)
        .filter(models.Appointment.doctor_id == doctor_id)
        .all()
    )
