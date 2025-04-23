from aiogram.fsm.state import State, StatesGroup

class RegistrationStates(StatesGroup):
    """Стани для процесу реєстрації"""
    waiting_for_gender = State()
    waiting_for_birth_date = State()

class ProfileStates(StatesGroup):
    """Стани для редагування профілю"""
    waiting_for_new_gender = State()
    waiting_for_new_birth_date = State()
    confirming_delete = State()

class IdeaStates(StatesGroup):
    """Стани для пропозиції ідей"""
    waiting_for_idea = State()

class AdminStates(StatesGroup):
    """Стани для адмін-функцій"""
    waiting_for_broadcast_text = State()
    waiting_for_broadcast_date = State()
    waiting_for_quote = State()