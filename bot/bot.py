import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.redis import RedisStorage2

from handlers.appointment import register_appointment_handlers
from config import BOT_TOKEN, REDIS_HOST, REDIS_PORT, REDIS_DB


async def main():
    logging.basicConfig(level=logging.INFO)

    bot = Bot(token=BOT_TOKEN)
    storage = RedisStorage2(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
    dp = Dispatcher(bot, storage=storage)

    register_appointment_handlers(dp)

    try:
        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())