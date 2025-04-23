from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_gender_keyboard():
    """Клавіатура для вибору статі"""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Чоловік", callback_data="male"))
    builder.add(InlineKeyboardButton(text="Жінка", callback_data="female"))
    return builder.as_markup()

def get_main_menu_keyboard():
    """Головне меню бота"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="📝 Редагувати дані", callback_data="edit_profile"))
    builder.row(InlineKeyboardButton(text="💡 Запропонувати ідею", callback_data="suggest_idea"))
    builder.row(InlineKeyboardButton(text="📊 Оновити таблицю", callback_data="update_table"))
    builder.row(InlineKeyboardButton(text="🔔 Налаштування нагадувань", callback_data="notification_settings"))
    return builder.as_markup()

def get_edit_profile_keyboard():
    """Клавіатура для редагування профілю"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="👤 Змінити стать", callback_data="change_gender"))
    builder.row(InlineKeyboardButton(text="📅 Змінити дату народження", callback_data="change_birth_date"))
    builder.row(InlineKeyboardButton(text="❌ Видалити всі дані", callback_data="delete_data"))
    builder.row(InlineKeyboardButton(text="↩️ Назад", callback_data="back_to_main"))
    return builder.as_markup()

def get_confirmation_keyboard():
    """Клавіатура підтвердження"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="✅ Підтвердити", callback_data="confirm_delete"))
    builder.row(InlineKeyboardButton(text="❌ Скасувати", callback_data="cancel_delete"))
    return builder.as_markup()

def get_notification_settings_keyboard(notifications_enabled):
    """Клавіатура налаштувань нагадувань"""
    status = "Увімкнені" if notifications_enabled else "Вимкнені"
    
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text=f"🔔 Нагадування: {status}", 
        callback_data="toggle_notifications"
    ))
    builder.row(InlineKeyboardButton(text="↩️ Назад", callback_data="back_to_main"))
    return builder.as_markup()

def get_admin_keyboard():
    """Клавіатура адмін-панелі"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats"))
    builder.row(InlineKeyboardButton(text="📨 Розсилка", callback_data="admin_broadcast"))
    builder.row(InlineKeyboardButton(text="💬 Змінити цитату", callback_data="update_quote"))
    return builder.as_markup()

def get_admin_broadcast_keyboard():
    """Клавіатура для розсилки повідомлень"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="📤 Відправити зараз", callback_data="send_broadcast_now"))
    builder.row(InlineKeyboardButton(text="⏰ Запланувати", callback_data="schedule_broadcast"))
    builder.row(InlineKeyboardButton(text="❌ Скасувати", callback_data="cancel_broadcast"))
    return builder.as_markup()