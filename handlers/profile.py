from aiogram import Router, F
from aiogram.types import CallbackQuery
from database.db import get_files_by_category_and_user

router = Router()

@router.callback_query(F.data.startswith("cat_"))
async def process_category(callback: CallbackQuery, db_user):
    category = callback.data.replace("cat_", "")
    user_id = db_user['id']
    
    if category == "my_info":
        response = f"👤 **Sizning ma'lumotlaringiz:**\n\n"
        response += f"Ism-Sharif: {db_user['full_name']}\n"
        response += f"Telegram ID: {db_user['tg_id']}\n"
        response += f"Holat: {'Tizim tasdiqlangan' if db_user['is_agreed'] else 'Tasdiqlanmagan'}"
        await callback.message.edit_text(response, parse_mode="Markdown")
        return
        
    # Fetch files for this category
    # 'id_card', 'class_file', 'textbook'
    files = await get_files_by_category_and_user(category, user_id)
    
    if not files:
        await callback.answer("Bu bo'limda hozircha fayllar yo'q.", show_alert=True)
        return
        
    from aiogram.utils.keyboard import InlineKeyboardBuilder

    builder = InlineKeyboardBuilder()
    
    for f in files:
        # Har bir fayl uchun alohida tugma yaratamiz
        builder.button(
            text=f"📄 {f['title']}", 
            callback_data=f"show_file_{f['id']}"
        )
    
    builder.adjust(1)  # Tugmalarni ustma-ust taxlash

    await callback.message.answer(
        f"📦 **Tanlangan bo'lim: {category}**\n\nKo'rmoqchi bo'lgan faylingizni tanlang:",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )
    
    
