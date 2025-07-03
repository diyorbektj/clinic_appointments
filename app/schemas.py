from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class DoctorBase(BaseModel):
    name: str = Field(..., description="ФИО врача")
    specialty: str = Field(..., description="Специализация")


class DoctorCreate(DoctorBase):
    pass


class DoctorResponse(DoctorBase):
    id: int

    class Config:
        from_attributes = True


class AppointmentBase(BaseModel):
    doctor_id: int
    patient_name: str
    patient_phone: str
    start_time: datetime
    end_time: datetime


class AppointmentCreate(AppointmentBase):
    pass


class AppointmentResponse(AppointmentBase):
    id: int
    doctor: DoctorResponse

    class Config:
        from_attributes = True
