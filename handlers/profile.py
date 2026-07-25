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
        
    await callback.message.answer(f"📦 Tanlangan bo'lim: {category}")
    for f in files:
        try:
            await callback.message.answer_document(f['file_id'], caption=f['title'])
        except Exception:
            try:
                await callback.message.answer_photo(f['file_id'], caption=f['title'])
            except:
                pass
    
    await callback.answer()
