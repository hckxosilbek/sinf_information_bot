from aiogram.fsm.state import StatesGroup, State

class AdminStates(StatesGroup):
    waiting_for_new_user_id = State()
    waiting_for_new_user_name = State()
    waiting_for_file = State()
    waiting_for_file_title = State()
    waiting_for_file_category = State()
    waiting_for_file_user_id = State()

class SearchStates(StatesGroup):
    waiting_for_student_name = State()
