from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from database.db import add_user, add_file
from keyboards.inline import get_admin_menu_kb, get_cancel_kb
from utils.states import AdminStates
import os
from dotenv import load_dotenv

load_dotenv()
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

router = Router()

def is_admin_check(message: Message) -> bool:
    return message.from_user.id == ADMIN_ID

@router.message(Command("admin"))
async def cmd_admin(message: Message):
    if not is_admin_check(message):
        return
    await message.answer("👨‍💻 Admin Panel:", reply_markup=get_admin_menu_kb())

@router.callback_query(F.data == "admin_add_user")
async def process_add_user(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    await state.set_state(AdminStates.waiting_for_new_user_id)
    await callback.message.edit_text("Yangi o'quvchining Telegram ID sini kiriting:", reply_markup=get_cancel_kb())

@router.message(AdminStates.waiting_for_new_user_id)
async def process_new_user_id(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Iltimos, faqat raqamli ID kiriting:")
        return
    await state.update_data(new_tg_id=int(message.text))
    await state.set_state(AdminStates.waiting_for_new_user_name)
    await message.answer("Endi o'quvchining To'liq Ism-Sharifini kiriting (Masalan: Tojiboyev Xosilbek):", reply_markup=get_cancel_kb())

@router.message(AdminStates.waiting_for_new_user_name)
async def process_new_user_name(message: Message, state: FSMContext):
    data = await state.get_data()
    tg_id = data['new_tg_id']
    full_name = message.text
    
    success = await add_user(tg_id, full_name)
    if success:
        await message.answer(f"✅ O'quvchi muvaffaqiyatli qo'shildi!\nID: {tg_id}\nIsm: {full_name}")
    else:
        await message.answer("❌ Xatolik yuz berdi. Balki bu ID bazada bordir?")
    await state.clear()

@router.callback_query(F.data == "admin_upload_file")
async def process_upload_file(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    await state.set_state(AdminStates.waiting_for_file)
    await callback.message.edit_text("Iltimos, fayl yoki rasmni yuboring:", reply_markup=get_cancel_kb())

@router.message(AdminStates.waiting_for_file, F.document | F.photo)
async def process_file(message: Message, state: FSMContext):
    if message.document:
        file_id = message.document.file_id
    elif message.photo:
        file_id = message.photo[-1].file_id
        
    await state.update_data(file_id=file_id)
    await state.set_state(AdminStates.waiting_for_file_title)
    await message.answer("Faylga nom bering:", reply_markup=get_cancel_kb())

@router.message(AdminStates.waiting_for_file_title)
async def process_file_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(AdminStates.waiting_for_file_category)
    await message.answer(
        "Kategoriyani kiriting:\nMasalan: `id_card`, `class_file`, `textbook`", 
        parse_mode="Markdown",
        reply_markup=get_cancel_kb()
    )

@router.message(AdminStates.waiting_for_file_category)
async def process_file_category(message: Message, state: FSMContext):
    await state.update_data(category=message.text)
    await state.set_state(AdminStates.waiting_for_file_user_id)
    await message.answer(
        "Agar bu fayl qaysidir o'quvchiga tegishli bo'lsa uning ID sini kiriting (DB ID, tg_id emas).\nAgar hammaga tegishli bo'lsa '0' yuboring:", 
        reply_markup=get_cancel_kb()
    )

@router.message(AdminStates.waiting_for_file_user_id)
async def process_file_user_id(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Iltimos, raqam kiriting:")
        return
        
    user_id = int(message.text)
    if user_id == 0:
        user_id = None
        
    data = await state.get_data()
    await add_file(data['file_id'], data['title'], data['category'], user_id)
    
    await message.answer("✅ Fayl muvaffaqiyatli saqlandi!")
    await state.clear()

@router.callback_query(F.data == "action_cancel")
async def cancel_action(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Amal bekor qilindi.")
import sqlite3
from aiogram import Bot, Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()

# O'zingizning Telegram admin ID raqamingizni yozing
ADMIN_ID = 123456789  # <-- O'z ID raqamingizni qo'ying


@router.message(Command("users"))
async def get_total_users(message: Message):
  # Xohlasangiz, bu buyruq faqat sizga (aminga) ishlashi uchun shart qo'shamiz:
  if message.from_user.id != ADMIN_ID:
    await message.answer("Bu buyruq faqat admin uchun!")
    return

  # Ma'lumotlar bazasiga ulanish (loyihangizdagi bazaga qarab yo'lini o'zgartiring)
  conn = sqlite3.connect("database.sqlite")  # yoki bazangiz nomi
  cursor = conn.cursor()

  try:
    # Bazadan foydalanuvchilar sonini sanab olish
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    await message.answer(f"👥 Botdagi jami foydalanuvchilar soni: {count} ta")
  except Exception as e:
    await message.answer(
        "Foydalanuvchilarni sanashda xatolik yuz berdi (baza yoki"
        " jadval topilmadi)."
    )
  finally:
    conn.close()