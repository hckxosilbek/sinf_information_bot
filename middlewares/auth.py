from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery, Update
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
        
        # Aiogram 3 da event Update ko'rinishida kelishi mumkin
        real_event = event
        if isinstance(event, Update):
            real_event = event.event  # Ichidagi Message yoki CallbackQuery ni ajratib olamiz

        user = None
        if isinstance(real_event, Message):
            user = real_event.from_user
        elif isinstance(real_event, CallbackQuery):
            user = real_event.from_user
            
        if not user:
            return await handler(event, data)
            
        # Bazadan foydalanuvchini tekshiramiz
        db_user = await get_user_by_tg_id(user.id)
        
        # Admin bo'lsa
        if user.id == ADMIN_ID:
            # Agar admin bazada hali yo'q bo'lsa ham bo'sh lug'at o'rnida o'tkazamiz
            data['db_user'] = db_user if db_user else {"id": user.id, "role": "admin"}
            return await handler(event, data)
            
        if not db_user:
            # Whitelist'da yo'q foydalanuvchi
            if isinstance(real_event, Message):
                await real_event.answer("🚫 Kirish taqiqlangan. Siz tizimga kiritilmagansiz.")
            elif isinstance(real_event, CallbackQuery):
                await real_event.answer("🚫 Kirish taqiqlangan.", show_alert=True)
            return  # Jarayonni to'xtatish
            
        # Handlerga db_user ma'lumotini biriktirish
        data['db_user'] = db_user
        
        return await handler(event, data)