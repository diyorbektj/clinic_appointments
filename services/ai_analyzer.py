import re

import aiohttp
import json
from typing import Dict
from config import OPENAI_API_KEY

def extract_json_from_markdown(text):
    # ```json va ``` orasidagi qismni ajratib olamiz
    pattern = r"```json\s*(\{.*?\})\s*```"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        json_str = match.group(1)
        return json.loads(json_str)  # stringni JSON ga o'giradi
    else:
        raise ValueError("JSON block not found")


async def analyze_symptoms(symptoms: str) -> Dict[str, str]:
    """Анализ симптомов с помощью ИИ"""

    prompt = f"""
    Проанализируй симптомы пациента и определи:
    1. Рекомендуемая специализация врача (терапевт, кардиолог, невролог, дерматолог и т.д.)
    2. Уровень срочности (низкий, средний, высокий)
    3. Краткое обоснование рекомендации

    Симптомы: {symptoms}

    Ответ строго в JSON формате:
    {{
        "specialty": "название специализации",
        "urgency": "уровень срочности", 
        "reasoning": "краткое обоснование"
    }}
    """

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 200,
        "temperature": 0.3
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data
        ) as response:
            result = await response.json()
            try:
                content = result["choices"][0]["message"]["content"]
                clean_json_str = extract_json_from_markdown(content)

                return clean_json_str
            except (KeyError, json.JSONDecodeError):
                # Fallback в случае ошибки ИИ
                return {
                    "specialty": "терапевт",
                    "urgency": "средний",
                    "reasoning": "Общие симптомы, рекомендую терапевта"
                }


# Альтернативная реализация с правилами
SYMPTOM_RULES = {
    "болит сердце|боль в груди|давление": {
        "specialty": "кардиолог",
        "urgency": "высокий"
    },
    "головная боль|мигрень|головокружение": {
        "specialty": "невролог",
        "urgency": "средний"
    },
    "сыпь|зуд|прыщи": {
        "specialty": "дерматолог",
        "urgency": "низкий"
    },
    "температура|кашель|насморк|горло": {
        "specialty": "терапевт",
        "urgency": "средний"
    }
}


def analyze_symptoms_rules(symptoms: str) -> Dict[str, str]:
    """Простой анализ по правилам"""
    symptoms_lower = symptoms.lower()

    for pattern, result in SYMPTOM_RULES.items():
        if any(keyword in symptoms_lower for keyword in pattern.split("|")):
            return result

    # По умолчанию - терапевт
    return {
        "specialty": "терапевт",
        "urgency": "средний",
        "reasoning": "Общие симптомы"
    }