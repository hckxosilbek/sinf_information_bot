import asyncio
import logging
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from database.db import init_db
from middlewares.auth import WhitelistMiddleware
from handlers import start, admin, search, profile

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

async def main():
    logging.basicConfig(level=logging.INFO)
    
    # Initialize DB
    await init_db()
    
    if not BOT_TOKEN:
        logging.error("BOT_TOKEN not found in .env!")
        return
        
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    
    # Register Middleware
    dp.message.middleware(WhitelistMiddleware())
    dp.callback_query.middleware(WhitelistMiddleware())
    
    # Register Routers
    dp.include_router(start.router)
    dp.include_router(admin.router)
    dp.include_router(profile.router)
    # Search router should be last because it catches general text
    dp.include_router(search.router)
    
    print("Bot is starting...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
