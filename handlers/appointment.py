from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from services.ai_analyzer import analyze_symptoms
from services.doctor_matcher import find_available_doctors
from services.appointment_api import create_appointment

class AppointmentStates(StatesGroup):
    waiting_symptoms = State()
    waiting_doctor_choice = State()
    waiting_name = State()
    waiting_phone = State()

def register_appointment_handlers(dp: Dispatcher):
    dp.register_message_handler(start_appointment, commands="start", state="*")
    dp.register_message_handler(process_symptoms, state=AppointmentStates.waiting_symptoms)
    dp.register_message_handler(process_doctor_choice, state=AppointmentStates.waiting_doctor_choice)
    dp.register_message_handler(process_name, state=AppointmentStates.waiting_name)
    dp.register_message_handler(process_phone, state=AppointmentStates.waiting_phone)

async def start_appointment(message: types.Message):
    await message.answer("👋 Привет! Я помогу записаться на прием к врачу. Расскажите, что вас беспокоит?")
    await AppointmentStates.waiting_symptoms.set()

async def process_symptoms(message: types.Message, state: FSMContext):
    symptoms = message.text
    print(symptoms)
    result = await analyze_symptoms(symptoms)
    print(result)
    doctors = await find_available_doctors(result["specialty"])

    if not doctors:
        await message.answer("😔 Нет доступных врачей. Попробуйте позже.")
        await state.finish()
        return

    text = f"🔍 На основе симптомов рекомендую:\nСпециалист: {result['specialty']}\n"
    for i, doc in enumerate(doctors, 1):
        time_range = f"{doc['start_time']} - {doc['end_time']}"
        text += f"{i}. {doc['name']} — {time_range}\n"

    await message.answer(text + "\nВыберите врача, отправив номер.")
    await state.update_data(doctors=doctors)
    await AppointmentStates.waiting_doctor_choice.set()

async def process_doctor_choice(message: types.Message, state: FSMContext):
    data = await state.get_data()
    doctors = data["doctors"]

    try:
        index = int(message.text) - 1
        selected = doctors[index]
    except:
        await message.answer("❌ Неверный номер. Попробуйте еще раз.")
        return

    await state.update_data(doctor=selected)
    await message.answer("Как вас зовут?")
    await AppointmentStates.waiting_name.set()

async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Ваш номер телефона?")
    await AppointmentStates.waiting_phone.set()

async def process_phone(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        phone = message.text

        appointment = await create_appointment({
            "doctor": data["doctor"],
            "name": data["name"],
            "phone": phone
        })

        await message.answer(
            f"✅ Запись создана!\n\n"
            f"👤 {data['name']}\n"
            f"👨‍⚕️ {data['doctor']['name']}\n"
            f"📅 {data['doctor']['start_time']}\n"
            f"📞 {phone}\n"
            f"🏥 Адрес: ул. Медицинская, 15"
        )
        await state.finish()

    except Exception as e:
        await message.answer(f"❌ Ошибка при создании записи: {str(e)}")


