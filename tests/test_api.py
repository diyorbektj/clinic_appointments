import pytest
from httpx import AsyncClient

from app import models
from app.database import Base, SessionLocal, engine
from app.main import app


@pytest.fixture(scope="module")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="module")
def db_session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


@pytest.mark.anyio
async def test_healthcheck():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


@pytest.mark.anyio
async def test_create_and_get_appointment(db_session):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        doctor = models.Doctor(name="Терапевт Иванов", specialty="терапевт")
        db_session.add(doctor)
        db_session.commit()
        db_session.refresh(doctor)

        # Запись к пациенту
        appointment_data = {
            "doctor_id": doctor.id,
            "patient_name": "Анна Иванова",
            "patient_phone": "+7-900-123-45-67",
            "start_time": "2025-07-04T10:00:00",
            "end_time": "2025-07-04T10:30:00",
        }

        # Создаем запись
        response = await ac.post("/appointments", json=appointment_data)
        assert response.status_code == 200
        data = response.json()
        assert data["doctor_id"] == doctor.id
        assert data["patient_name"] == "Анна Иванова"

        appointment_id = data["id"]

        # Получаем запись
        response = await ac.get(f"/appointments/{appointment_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["patient_name"] == "Анна Иванова"


@pytest.mark.anyio
async def test_uniqueness_constraint(db_session):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Врач
        doctor = models.Doctor(name="Кардиолог Петров", specialty="кардиолог")
        db_session.add(doctor)
        db_session.commit()
        db_session.refresh(doctor)

        appointment_data = {
            "doctor_id": doctor.id,
            "patient_name": "Пациент 1",
            "patient_phone": "+7-900-111-11-11",
            "start_time": "2025-07-05T11:00:00",
            "end_time": "2025-07-05T11:30:00",
        }
        # Первая запись — успешна
        response = await ac.post("/appointments", json=appointment_data)
        assert response.status_code == 200

        # Вторая запись с тем же doctor_id и start_time — должна вызвать ошибку
        response = await ac.post("/appointments", json=appointment_data)
        assert response.status_code == 400
        assert "Doctor is already booked" in response.json()["detail"]
