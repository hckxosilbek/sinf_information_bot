from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject
from typing import Callable, Dict, Any, Awaitable
from database.db import get_user_by_tg_id
import os
from dotenv import load_dotenv

load_dotenv()
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

class WhitelistMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        
        # Get user from event
        user = None
        if isinstance(event, Message):
            user = event.from_user
        elif isinstance(event, CallbackQuery):
            user = event.from_user
            
        if not user:
            return await handler(event, data)
            
        # Check database
        db_user = await get_user_by_tg_id(user.id)
        
        # Auto-allow owner if they are not in DB yet (for initial setup)
        if user.id == ADMIN_ID:
            data['db_user'] = db_user
            return await handler(event, data)
            
        if not db_user:
            # User is not whitelisted
            if isinstance(event, Message):
                await event.answer("🚫 Kirish taqiqlangan. Siz tizimga kiritilmagansiz.")
            elif isinstance(event, CallbackQuery):
                await event.answer("🚫 Kirish taqiqlangan.", show_alert=True)
            return # Stop processing
            
        # Add user data to handler kwargs
        data['db_user'] = db_user
        
        return await handler(event, data)
