from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from database.db import get_user_by_name, get_files_by_category_and_user
from utils.states import SearchStates
from keyboards.inline import get_cancel_kb

router = Router()

@router.callback_query(F.data == "action_search")
async def action_search(callback: CallbackQuery, state: FSMContext):
    await state.set_state(SearchStates.waiting_for_student_name)
    await callback.message.edit_text(
        "🔍 O'quvchi ismini yoki familiyasini kiriting:",
        reply_markup=get_cancel_kb()
    )

@router.message(SearchStates.waiting_for_student_name)
async def process_search_name(message: Message, state: FSMContext):
    name_query = message.text
    users = await get_user_by_name(name_query)
    
    if not users:
        await message.answer("Bunday o'quvchi topilmadi. Qaytadan urinib ko'ring yoki /start orqali menyuga qayting.")
        return
        
    await state.clear()
    
    for user in users:
        user_id = user['id']
        full_name = user['full_name']
        
        # Fetch their files
        id_cards = await get_files_by_category_and_user('id_card', user_id)
        class_files = await get_files_by_category_and_user('class_file', user_id)
        
        response = f"👤 **Talaba:** {full_name}\n"
        response += f"🔢 **DB ID:** {user_id}\n\n"
        
        if id_cards:
            response += "𪪪 **ID Kartalar:** Mavjud\n"
        else:
            response += "𪪪 **ID Kartalar:** Yo'q\n"
            
        if class_files:
            response += f"📁 **Sinf Fayllari:** {len(class_files)} ta topildi\n"
            
        await message.answer(response, parse_mode="Markdown")
        
        # Send ID Cards if exist
        for card in id_cards:
            try:
                await message.answer_photo(card['file_id'], caption=f"ID Karta: {card['title']}")
            except Exception:
                try:
                    await message.answer_document(card['file_id'], caption=f"ID Karta (Hujjat): {card['title']}")
                except:
                    pass
                    
        # Send Class files
        for f in class_files:
            try:
                await message.answer_document(f['file_id'], caption=f['title'])
            except:
                pass

@router.message(F.text)
async def quick_search(message: Message, state: FSMContext, db_user):
    # This handler catches any text outside FSM.
    # It acts as a quick search.
    if not db_user['is_agreed']:
        return
        
    # We can reuse the search logic
    await process_search_name(message, state)
