import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.redis import RedisStorage2

from handlers import register_handlers
from config import BOT_TOKEN, REDIS_URL


async def main():
    logging.basicConfig(level=logging.INFO)

    bot = Bot(token=BOT_TOKEN)
    storage = RedisStorage2.from_url(REDIS_URL)
    dp = Dispatcher(bot, storage=storage)

    register_handlers(dp)

    try:
        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())