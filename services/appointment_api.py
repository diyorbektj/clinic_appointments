import os
from datetime import datetime

import aiohttp

API_URL = os.getenv("API_URL")
if not API_URL:
    raise ValueError("API_URL environment variable is not set")

API_URL = API_URL.rstrip("/") + "/appointments"  # API_URL oxirida / bo'lmasligi uchun


async def create_appointment(data: dict) -> dict:
    print(data)
    payload = {
        "doctor_id": data["doctor"]["id"],
        "patient_name": data["name"],
        "patient_phone": data["phone"],
        "start_time": convert_to_iso(data["doctor"]["start_time"]),
        "end_time": convert_to_iso(data["doctor"]["end_time"]),
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(API_URL, json=payload) as response:
            if response.status == 200 or response.status == 201:
                return await response.json()
            else:
                text = await response.text()
                raise Exception(f"API error {response.status}: {text}")


def convert_to_iso(time_str: str) -> str:
    """
    Converts '4 июля 10:00' to ISO format string: '2025-07-04T10:00:00'
    """
    months = {
        "января": "01",
        "февраля": "02",
        "марта": "03",
        "апреля": "04",
        "мая": "05",
        "июня": "06",
        "июля": "07",
        "августа": "08",
        "сентября": "09",
        "октября": "10",
        "ноября": "11",
        "декабря": "12",
    }

    parts = time_str.strip().split()
    if len(parts) != 3:
        raise ValueError(f"Incorrect time format: {time_str}")

    day = parts[0].zfill(2)
    month = months.get(parts[1].lower())
    if not month:
        raise ValueError(f"Unknown month name: {parts[1]}")

    hour, minute = parts[2].split(":")
    year = datetime.now().year
    iso_str = f"{year}-{month}-{day} {hour}:{minute}:00"
    return iso_str

    # ISO8601 format: YYYY-MM-DDTHH:MM:SS
