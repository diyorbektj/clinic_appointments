from fastapi import FastAPI, HTTPException, Depends, Query
from sqlalchemy import orm
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional

from app.database import SessionLocal, engine, Base
from app import models, schemas, crud
import uvicorn
from app.models import Doctor

orm.configure_mappers()
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Clinic API")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def startup_event():
    from app.models import Doctor, Appointment  # to‘liq import qilsin
    Base.metadata.create_all(bind=engine)

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# --- Appointments endpoints ---
@app.post("/appointments", response_model=schemas.AppointmentResponse)
def create_appointment_endpoint(appointment: schemas.AppointmentCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_appointment(db, appointment)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Doctor is already booked at this time")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/appointments/{appointment_id}", response_model=schemas.AppointmentResponse)
def get_appointment_endpoint(appointment_id: int, db: Session = Depends(get_db)):
    appointment = crud.get_appointment(db, appointment_id)
    if appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointment

@app.get("/appointments", response_model=List[schemas.AppointmentResponse])
def get_appointments(
    doctor_id: Optional[int] = Query(None, description="ID врача (необязательно)"),
    db: Session = Depends(get_db)
):
    if doctor_id:
        return crud.get_appointments_by_doctor(db, doctor_id=doctor_id)
    else:
        # Agar doctor_id yo‘q bo‘lsa, hamma appointmentlarni qaytaradi
        return db.query(models.Appointment).all()


# --- Doctor endpoints ---
@app.post("/doctors", response_model=schemas.DoctorResponse)
def create_doctor_endpoint(doctor: schemas.DoctorCreate, db: Session = Depends(get_db)):
    return crud.create_doctor(db, doctor)

@app.get("/doctors/{doctor_id}", response_model=schemas.DoctorResponse)
def get_doctor_endpoint(doctor_id: int, db: Session = Depends(get_db)):
    doctor = crud.get_doctor(db, doctor_id)
    if doctor is None:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor

@app.get("/doctors", response_model=List[schemas.DoctorResponse])
def list_doctors(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    return crud.get_all_doctors(db, skip=skip, limit=limit)


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)