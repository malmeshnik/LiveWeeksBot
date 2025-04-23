from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from utils.keyboards import get_gender_keyboard, get_main_menu_keyboard
from utils.states import RegistrationStates
from database.db_operations import save_user, get_user
from utils.image_generator import generate_life_table

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """Початок роботи бота"""
    user_id = message.from_user.id
    user = await get_user(user_id)
    
    if user:
        # Якщо користувач вже зареєстрований
        await message.answer(
            f"Раді бачити вас знову, {user.first_name}!",
            reply_markup=get_main_menu_keyboard()
        )
    else:
        # Новий користувач
        await message.answer(
            "Вітаю! Я бот, який допоможе вам усвідомити цінність часу. "
            "Я покажу скільки тижнів ви вже прожили і скільки приблизно залишилось.\n\n"
            "Для початку, вкажіть вашу стать:",
            reply_markup=get_gender_keyboard()
        )
        await state.set_state(RegistrationStates.waiting_for_gender)

@router.callback_query(RegistrationStates.waiting_for_gender, F.data.in_(["male", "female"]))
async def process_gender(callback: CallbackQuery, state: FSMContext):
    """Обробка вибору статі"""
    await callback.answer()
    gender = callback.data
    
    await state.update_data(gender=gender)
    await callback.message.answer(
        "Дякую! Тепер введіть дату вашого народження у форматі ДД.ММ.РРРР\n"
        "Наприклад: 01.01.1990"
    )
    await state.set_state(RegistrationStates.waiting_for_birth_date)

@router.message(RegistrationStates.waiting_for_birth_date)
async def process_birth_date(message: Message, state: FSMContext):
    """Обробка введення дати народження"""
    try:
        from datetime import datetime
        birth_date = datetime.strptime(message.text, "%d.%m.%Y").date()
        
        user_data = await state.get_data()
        gender = user_data["gender"]
        
        # Зберігаємо користувача в БД
        await save_user(
            user_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            gender=gender,
            birth_date=birth_date
        )
        
        # Генеруємо та відправляємо таблицю
        table_image = generate_life_table(birth_date, gender)
        
        # Розраховуємо вік у роках та днях
        today = datetime.now().date()
        total_days = (today - birth_date).days
        years = total_days // 365
        remaining_days = total_days % 365
        
        # Розраховуємо прожиті тижні
        lived_weeks = total_days // 7
        
        # Загальна кількість днів життя (залежно від статі)
        total_life_days = 72 * 365 if gender == 'female' else 66 * 365
        days_left = total_life_days - total_days
        
        await message.answer_photo(
            photo=FSInputFile(table_image),
            caption=f"{message.from_user.first_name}, ти прожив(ла) свій {lived_weeks}-й тиждень!\n"
                    f"Тобі: {years} років, {remaining_days} днів\n"
                    f"Жити залишилося всього {days_left} днів!\n\n"
                    f"Час минає швидше, ніж ми думаємо...",
            reply_markup=get_main_menu_keyboard()
        )
        
        await state.clear()
        
    except ValueError:
        await message.answer(
            "Некоректний формат дати. Будь ласка, використовуйте формат ДД.ММ.РРРР\n"
            "Наприклад: 01.01.1990"
        )

def register_handlers(dp):
    dp.include_router(router)