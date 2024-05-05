import asyncio
import logging
import sys

import config
from aiogram import Bot, Dispatcher
from routers import router as commands_router

logging.basicConfig(level=logging.INFO, stream=sys.stdout)


dp = Dispatcher()
bot = Bot(token=config.TG_BOT_TOKEN)


# инициализация бота
async def main():
    dp.include_routers(
        commands_router,
    )
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())