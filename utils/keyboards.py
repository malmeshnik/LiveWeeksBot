from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_gender_keyboard():
    """Клавіатура для вибору статі"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Чоловік"),
            KeyboardButton(text="Жінка")]
        ],
        resize_keyboard=True
    )

def get_main_menu_keyboard():
    """Головне меню бота"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📝 Редагувати дані"),
            KeyboardButton(text="💡 Запропонувати ідею")]
        ],
        resize_keyboard=True
    )

def get_edit_profile_keyboard():
    """Клавіатура для редагування профілю"""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="👤 Змінити стать", callback_data="change_gender"))
    builder.row(InlineKeyboardButton(text="📅 Змінити дату народження", callback_data="change_birth_date"))
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