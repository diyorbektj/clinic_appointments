from datetime import datetime, timedelta

import aiohttp

API_BASE_URL = "http://localhost:8000"

WORK_START_HOUR = 9
WORK_END_HOUR = 17
SLOT_DURATION_MINUTES = 30


async def find_available_doctors(specialty: str) -> list:
    today = datetime(2025, 7, 4)

    async with aiohttp.ClientSession() as session:
        # 1. Doctorlar ro‘yxatini olish
        async with session.get(f"{API_BASE_URL}/doctors") as resp:
            all_doctors = await resp.json()

        # 2. Specialty bo‘yicha filter
        matched_doctors = [
            d for d in all_doctors if d["specialty"].lower() == specialty.lower()
        ]
        available_doctors = []

        for doctor in matched_doctors:
            doctor_id = doctor["id"]

            # 3. Shu doctorning appointmentlarini olish
            async with session.get(
                f"{API_BASE_URL}/appointments?doctor_id={doctor_id}"
            ) as resp:
                appointments = await resp.json()

            # 4. Band vaqtlar ro‘yxatini to‘plash
            busy_times = [
                (
                    datetime.fromisoformat(a["start_time"]),
                    datetime.fromisoformat(a["end_time"]),
                )
                for a in appointments
            ]

            # 5. Ish vaqtida bo‘sh slotlar yasash
            free_slots = []
            current_time = today.replace(hour=WORK_START_HOUR, minute=0, second=0)

            end_of_day = today.replace(hour=WORK_END_HOUR, minute=0, second=0)

            while current_time + timedelta(minutes=SLOT_DURATION_MINUTES) <= end_of_day:
                slot_start = current_time
                slot_end = current_time + timedelta(minutes=SLOT_DURATION_MINUTES)

                # Check if this slot overlaps with any busy time
                if not any(
                    slot_start < b_end and slot_end > b_start
                    for b_start, b_end in busy_times
                ):
                    free_slots.append(
                        {
                            "id": doctor_id,
                            "name": doctor["name"],
                            "start_time": slot_start.strftime("%d июля %H:%M"),
                            "end_time": slot_end.strftime("%d июля %H:%M"),
                        }
                    )

                current_time += timedelta(minutes=SLOT_DURATION_MINUTES)

            # 6. Faqat agar bo‘sh slotlar mavjud bo‘lsa — ro‘yxatga qo‘shamiz
            if free_slots:
                available_doctors.extend(free_slots)
        return available_doctors
