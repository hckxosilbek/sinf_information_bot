from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from database.db import update_user_agreement, add_user
from keyboards.inline import get_agreement_kb, get_main_menu_kb
import os
from dotenv import load_dotenv

load_dotenv()
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

router = Router()

RULES_TEXT = """
📜 **Sinf qoidalari va Tartiblar:**

1. Botdan faqat ruxsat etilgan o'quvchilar foydalanishi mumkin.
2. Ma'lumotlarni tarqatish qat'iyan man etiladi.
3. ID kartangizni doim o'zingiz bilan olib yuring.
4. O'z vaqtida darsiklarni yuklab oling.

Ushbu qoidalarni o'qib chiqib, rozi bo'lsangiz quyidagi tugmani bosing.
"""

@router.message(CommandStart())
async def cmd_start(message: Message, db_user):
    # If admin is starting for the first time and not in DB
    if message.from_user.id == ADMIN_ID and not db_user:
        await add_user(tg_id=ADMIN_ID, full_name="Admin", is_admin=True)
        await message.answer("Siz Admin sifatida ro'yxatdan o'tdingiz!\n/admin buyrug'idan foydalanishingiz mumkin.")
        return
        
    if not db_user:
        # This shouldn't happen due to middleware, but just in case
        return

    # Check if agreed
    if not db_user['is_agreed']:
        await message.answer(RULES_TEXT, reply_markup=get_agreement_kb(), parse_mode="Markdown")
    else:
        await message.answer("Asosiy menyu:", reply_markup=get_main_menu_kb())

@router.callback_query(F.data == "agree_rules")
async def process_agreement(callback: CallbackQuery, db_user):
    await update_user_agreement(callback.from_user.id, True)
    await callback.message.edit_text("✅ Qoidalar qabul qilindi!\n\nAsosiy menyu:", reply_markup=get_main_menu_kb())
    await callback.answer("Muvaffaqiyatli!")
