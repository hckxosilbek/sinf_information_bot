import asyncio
import logging
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher

from database.db import init_db
from middlewares.auth import WhitelistMiddleware  # Middleware import qilingan
from handlers import start, admin, search, profile, class_files

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

dp = Dispatcher()

async def main():
    logging.basicConfig(level=logging.INFO)

    # Bazani ishga tushirish
    await init_db()

    if not BOT_TOKEN:
        logging.error("BOT_TOKEN not found in .env!")
        return

    bot = Bot(token=BOT_TOKEN)

    # 🟢 MANA SHU QATORNI QO'SHING (Middleware'ni ulash):
    dp.update.outer_middleware(WhitelistMiddleware())

    # Routerlarni ulash
    dp.include_router(class_files.router)
    dp.include_router(start.router)
    dp.include_router(admin.router)
    dp.include_router(search.router)
    dp.include_router(profile.router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())