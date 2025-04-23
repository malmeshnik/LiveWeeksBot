from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext

from utils.keyboards import (
    get_main_menu_keyboard, 
    get_edit_profile_keyboard, 
    get_gender_keyboard,
    get_confirmation_keyboard,
    get_notification_settings_keyboard
)
from utils.states import ProfileStates
from database.db_operations import (
    get_user, 
    update_user_gender, 
    update_user_birth_date, 
    delete_user_data,
    toggle_notifications
)
from utils.image_generator import generate_life_table
from datetime import datetime

router = Router()

@router.callback_query(F.data == "edit_profile")
async def edit_profile(callback: CallbackQuery):
    """Відкриття меню редагування профілю"""
    await callback.answer()
    await callback.message.answer(
        "Що саме ви хочете змінити?",
        reply_markup=get_edit_profile_keyboard()
    )

@router.callback_query(F.data == "change_gender")
async def change_gender(callback: CallbackQuery, state: FSMContext):
    """Зміна статі користувача"""
    await callback.answer()
    await callback.message.answer(
        "Виберіть вашу стать:",
        reply_markup=get_gender_keyboard()
    )
    await state.set_state(ProfileStates.waiting_for_new_gender)

@router.callback_query(ProfileStates.waiting_for_new_gender, F.data.in_(["male", "female"]))
async def process_new_gender(callback: CallbackQuery, state: FSMContext):
    """Обробка нової статі"""
    await callback.answer()
    gender = callback.data
    user_id = callback.from_user.id
    
    # Оновлюємо стать у БД
    await update_user_gender(user_id, gender)
    
    # Отримуємо оновлені дані користувача
    user = await get_user(user_id)
    
    # Генеруємо оновлену таблицю
    table_image = generate_life_table(user.birth_date, gender)
    
    # Розраховуємо вік та інші дані
    today = datetime.now().date()
    total_days = (today - user.birth_date).days
    years = total_days // 365
    remaining_days = total_days % 365
    
    # Розраховуємо прожиті тижні
    lived_weeks = total_days // 7
    
    # Загальна кількість днів життя (залежно від статі)
    total_life_days = 72 * 365 if gender == 'female' else 66 * 365
    days_left = total_life_days - total_days
    
    await callback.message.answer_photo(
        photo=FSInputFile(table_image),
        caption=f"{callback.from_user.first_name}, ти прожив(ла) свій {lived_weeks}-й тиждень!\n"
                f"Тобі: {years} років, {remaining_days} днів\n"
                f"Жити залишилося всього {days_left} днів!\n\n"
                f"Час минає швидше, ніж ми думаємо...",
        reply_markup=get_main_menu_keyboard()
    )
    
    await state.clear()

@router.callback_query(F.data == "change_birth_date")
async def change_birth_date(callback: CallbackQuery, state: FSMContext):
    """Зміна дати народження"""
    await callback.answer()
    await callback.message.answer(
        "Введіть вашу нову дату народження у форматі ДД.ММ.РРРР\n"
        "Наприклад: 01.01.1990"
    )
    await state.set_state(ProfileStates.waiting_for_new_birth_date)

@router.message(ProfileStates.waiting_for_new_birth_date)
async def process_new_birth_date(message: Message, state: FSMContext):
    """Обробка нової дати народження"""
    try:
        birth_date = datetime.strptime(message.text, "%d.%m.%Y").date()
        user_id = message.from_user.id
        
        # Оновлюємо дату народження у БД
        await update_user_birth_date(user_id, birth_date)
        
        # Отримуємо оновлені дані користувача
        user = await get_user(user_id)
        
        # Генеруємо оновлену таблицю
        table_image = generate_life_table(birth_date, user.gender)
        
        # Розраховуємо вік та інші дані
        today = datetime.now().date()
        total_days = (today - birth_date).days
        years = total_days // 365
        remaining_days = total_days % 365
        
        # Розраховуємо прожиті тижні
        lived_weeks = total_days // 7
        
        # Загальна кількість днів життя (залежно від статі)
        total_life_days = 72 * 365 if user.gender == 'female' else 66 * 365
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

@router.callback_query(F.data == "delete_data")
async def confirm_delete_data(callback: CallbackQuery, state: FSMContext):
    """Підтвердження видалення даних"""
    await callback.answer()
    await callback.message.answer(
        "⚠️ Ви впевнені, що хочете видалити всі свої дані? "
        "Ця дія не може бути скасована.",
        reply_markup=get_confirmation_keyboard()
    )
    await state.set_state(ProfileStates.confirming_delete)

@router.callback_query(ProfileStates.confirming_delete, F.data == "confirm_delete")
async def process_delete_data(callback: CallbackQuery, state: FSMContext):
    """Видалення даних користувача"""
    await callback.answer()
    user_id = callback.from_user.id
    
    # Видаляємо дані користувача
    await delete_user_data(user_id)
    
    await callback.message.answer(
        "Ваші дані успішно видалено. "
        "Якщо ви захочете скористатися ботом знову, "
        "просто відправте команду /start."
    )
    
    await state.clear()

@router.callback_query(ProfileStates.confirming_delete, F.data == "cancel_delete")
async def cancel_delete_data(callback: CallbackQuery, state: FSMContext):
    """Скасування видалення даних"""
    await callback.answer()
    await callback.message.answer(
        "Видалення даних скасовано.",
        reply_markup=get_main_menu_keyboard()
    )
    await state.clear()

@router.callback_query(F.data == "back_to_main")
async def back_to_main_menu(callback: CallbackQuery):
    """Повернення до головного меню"""
    await callback.answer()
    await callback.message.answer(
        "Головне меню:",
        reply_markup=get_main_menu_keyboard()
    )

@router.callback_query(F.data == "update_table")
async def update_life_table(callback: CallbackQuery):
    """Оновлення таблиці життя"""
    await callback.answer()
    user_id = callback.from_user.id
    
    # Отримуємо дані користувача
    user = await get_user(user_id)
    
    if not user:
        await callback.message.answer(
            "Не вдалося знайти ваші дані. Будь ласка, почніть знову з команди /start."
        )
        return
    
    # Генеруємо оновлену таблицю
    table_image = generate_life_table(user.birth_date, user.gender)
    
    # Розраховуємо вік та інші дані
    today = datetime.now().date()
    total_days = (today - user.birth_date).days
    years = total_days // 365
    remaining_days = total_days % 365
    
    # Розраховуємо прожиті тижні
    lived_weeks = total_days // 7
    
    # Загальна кількість днів життя (залежно від статі)
    total_life_days = 72 * 365 if user.gender == 'female' else 66 * 365
    days_left = total_life_days - total_days
    
    await callback.message.answer_photo(
        photo=FSInputFile(table_image),
        caption=f"{callback.from_user.first_name}, ти прожив(ла) свій {lived_weeks}-й тиждень!\n"
                f"Тобі: {years} років, {remaining_days} днів\n"
                f"Жити залишилося всього {days_left} днів!\n\n"
                f"Час минає швидше, ніж ми думаємо...",
        reply_markup=get_main_menu_keyboard()
    )

@router.callback_query(F.data == "notification_settings")
async def notification_settings(callback: CallbackQuery):
    """Налаштування нагадувань"""
    await callback.answer()
    user_id = callback.from_user.id
    
    # Отримуємо дані користувача
    user = await get_user(user_id)
    
    if not user:
        await callback.message.answer(
            "Не вдалося знайти ваші дані. Будь ласка, почніть знову з команди /start."
        )
        return
    
    await callback.message.answer(
        "Налаштування нагадувань:",
        reply_markup=get_notification_settings_keyboard(user.notifications_enabled)
    )

@router.callback_query(F.data == "toggle_notifications")
async def toggle_user_notifications(callback: CallbackQuery):
    """Увімкнути/вимкнути нагадування"""
    await callback.answer()
    user_id = callback.from_user.id
    
    # Отримуємо дані користувача
    user = await get_user(user_id)
    
    if not user:
        await callback.message.answer(
            "Не вдалося знайти ваші дані. Будь ласка, почніть знову з команди /start."
        )
        return
    
    # Змінюємо стан нагадувань на протилежний
    new_state = not user.notifications_enabled
    await toggle_notifications(user_id, new_state)
    
    status = "увімкнено" if new_state else "вимкнено"
    await callback.message.answer(
        f"Щотижневі нагадування {status}!",
        reply_markup=get_notification_settings_keyboard(new_state)
    )

def register_handlers(dp):
    dp.include_router(router)