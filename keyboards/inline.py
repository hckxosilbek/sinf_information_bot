from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_agreement_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Tushundim va Rozi", callback_data="agree_rules")]
        ]
    )

def get_main_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="𪪪 ID Kartalar", callback_data="cat_id_card"),
                InlineKeyboardButton(text="📁 Sinf Fayllari", callback_data="cat_class_file")
            ],
            [
                InlineKeyboardButton(text="📚 Darsliklar", callback_data="cat_textbook"),
                InlineKeyboardButton(text="👤 Mening Ma'lumotlarim", callback_data="cat_my_info")
            ],
            [
                InlineKeyboardButton(text="🔍 Qidiruv", callback_data="action_search")
            ]
        ]
    )

def get_admin_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="➕ Talaba qo'shish", callback_data="admin_add_user"),
                InlineKeyboardButton(text="📤 Fayl yuklash", callback_data="admin_upload_file")
            ]
        ]
    )

def get_cancel_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="action_cancel")]
        ]
    )
