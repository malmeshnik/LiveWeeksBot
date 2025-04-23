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
            "Привіт! Я створений, щоб нагадати: час — це життя. Порахуй зі мною, скільки тижнів ти вже прожив(ла) і скільки лишилось. "

            "Для коректної роботи, будь ласка, вкажіть вашу стать:",
            reply_markup=get_gender_keyboard()
        )
        await state.set_state(RegistrationStates.waiting_for_gender)

@router.message(RegistrationStates.waiting_for_gender, F.text.in_(["Чоловік", "Жінка"]))
async def process_gender(message: Message, state: FSMContext):
    """Обробка вибору статі"""
    gender = message.text
    
    await state.update_data(gender=gender)
    await message.answer(
        """Залишилось вказати вашу дату народження. Формат: ДД.ММ.РРРР
Приклад: 22.02.2002"""
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
        lived_weeks = remaining_days // 7
        remaining_days = remaining_days - lived_weeks * 7
        
        # Розраховуємо прожиті тижні
        lived_weeks = total_days // 7
        
        # Загальна кількість днів життя (залежно від статі)
        total_life_days = 72 * 365 if gender == 'female' else 66 * 365
        days_left = total_life_days - total_days

        if gender == "Чоловік":
            mess = f'''Середній вік чоловіків в Україні 66 років!
Ви прожили вже (рік), (тижні), (дні).

Вражає?
Покажіть друзям свою таблицю життя — пересилайте це повідомлення або поділіться ботом: @(юзер)'''
        else:
            mess = f'''Середній вік жінок в Україні 72 роки!
Ви прожили вже {years} років, {lived_weeks} тижнів,  {remaining_days} днів.

Вражає?
Покажіть друзям свою таблицю життя — пересилайте це повідомлення або поділіться ботом: @(юзер)'''
        
        await message.answer(
            text=mess,
            reply_markup=get_main_menu_keyboard()
        )

        await message.answer_photo(
            photo=FSInputFile(table_image)
        )

        await message.answer(
            text='Я щотижня надсилатиму вам оновлену таблицю. Побачимось за тиждень!'
        )
        
        await state.clear()
        
    except ValueError:
        await message.answer(
            "Некоректний формат дати. Будь ласка, використовуйте формат ДД.ММ.РРРР\n"
            "Наприклад: 01.01.1990"
        )

def register_handlers(dp):
    dp.include_router(router)