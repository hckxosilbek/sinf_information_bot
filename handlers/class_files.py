from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Database obyekti joylashuvini moslang (masalan: database/db.py bo'lsa)
from database.db import db  

router = Router()

# "Sinf Fayllari" tugmasi bosilganda
@router.message(F.text.in_(["📦 Sinf Fayllari", "Sinf Fayllari", "class_file"]))
async def show_class_files(message: Message):
    files = await db.get_all_class_files() 
    
    if not files:
        await message.answer("📁 Hozircha hech qanday fayl mavjud emas.")
        return

    builder = InlineKeyboardBuilder()
    
    for file in files:
        file_id = file[0]
        file_title = file[1]
        
        builder.button(
            text=f"📄 {file_title}", 
            callback_data=f"show_file_{file_id}"
        )
    
    builder.adjust(1)

    await message.answer(
        "📂 **Sinf fayllari ro'yxati:**\n\nKerakli faylni ko'rish uchun quyidagi tugmalardan birini bosing:",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )

# Tugmalardan biri bosilganda faylni yuborish
@router.callback_query(F.data.startswith("show_file_"))
async def send_selected_file(call: CallbackQuery):
    file_db_id = int(call.data.split("_")[2])
    file_data = await db.get_file_by_id(file_db_id)
    
    if not file_data:
        await call.answer("❌ Fayl topilmadi!", show_alert=True)
        return

    await call.answer()

    file_title = file_data[1]
    telegram_file_id = file_data[2]
    file_type = file_data[3] if len(file_data) > 3 else 'photo'

    if file_type == 'photo':
        await call.message.answer_photo(
            photo=telegram_file_id,
            caption=f"📄 **{file_title}**",
            parse_mode="Markdown"
        )
    else:
        await call.message.answer_document(
            document=telegram_file_id,
            caption=f"📄 **{file_title}**",
            parse_mode="Markdown"
        )