from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from utils.keyboards import get_admin_keyboard, get_admin_broadcast_keyboard
from utils.states import AdminStates
from database.db_operations import is_admin, get_stats, get_all_active_users, update_quote
from config import ADMIN_IDS
from datetime import datetime

router = Router()

@router.message(Command("admin"))
async def cmd_admin(message: Message):
    """Вхід в адмін-панель"""
    if message.from_user.id in ADMIN_IDS:
        await message.answer(
            "Вітаю в адмін-панелі!",
            reply_markup=get_admin_keyboard()
        )
    else:
        await message.answer("У вас немає доступу до цієї команди.")

@router.callback_query(F.data == "admin_stats")
async def process_admin_stats(callback: CallbackQuery):
    """Показує статистику користувачів"""
    if callback.from_user.id in ADMIN_IDS:
        await callback.answer()
        
        stats = await get_stats()
        total_users = stats['total_users']
        active_users = stats['active_users']
        male_count = stats['male_count']
        female_count = stats['female_count']
        avg_age = stats['avg_age']
        
        await callback.message.answer(
            f"📊 <b>Статистика користувачів</b>\n\n"
            f"👥 Всього користувачів: {total_users}\n"
            f"✅ Активні користувачі: {active_users}\n"
            f"👨 Чоловіки: {male_count} ({male_count/total_users*100:.1f}%)\n"
            f"👩 Жінки: {female_count} ({female_count/total_users*100:.1f}%)\n"
            f"🎂 Середній вік: {avg_age:.1f} років"
        )
    else:
        await callback.answer("У вас немає доступу.", show_alert=True)

@router.callback_query(F.data == "admin_broadcast")
async def process_admin_broadcast(callback: CallbackQuery, state: FSMContext):
    """Підготовка до розсилки повідомлень"""
    if callback.from_user.id in ADMIN_IDS:
        await callback.answer()
        await callback.message.answer(
            "Введіть текст розсилки:\n\n"
            "Ви можете використовувати HTML форматування:\n"
            "- <b>жирний</b>\n"
            "- <i>курсив</i>\n"
            "- <a href='http://example.com'>посилання</a>"
        )
        await state.set_state(AdminStates.waiting_for_broadcast_text)
    else:
        await callback.answer("У вас немає доступу.", show_alert=True)

@router.message(AdminStates.waiting_for_broadcast_text)
async def process_broadcast_text(message: Message, state: FSMContext):
    if message.from_user.id in ADMIN_IDS:
        if message.photo:
            file = await message.bot.download(message.photo[-1])
            photo_bytes = file.read()
            await state.update_data({
                "broadcast_type": "photo",
                "photo_bytes": photo_bytes,
                "caption": message.caption or ""
            })
        else:
            await state.update_data({
                "broadcast_type": "text",
                "text": message.text
            })

        await message.answer("Виберіть дію:", reply_markup=get_admin_broadcast_keyboard())

@router.callback_query(F.data == "send_broadcast_now")
async def send_broadcast_now(callback: CallbackQuery, state: FSMContext):
    """Відправка розсилки негайно (текст або фото)"""
    if callback.from_user.id in ADMIN_IDS:
        await callback.answer()

        user_data = await state.get_data()
        broadcast_type = user_data.get("broadcast_type")

        users = await get_all_active_users()
        sent_count = 0
        errors_count = 0

        await callback.message.answer("Розпочато розсилку...")

        for user in users:
            try:
                if broadcast_type == "photo":
                    photo_bytes = user_data["photo_bytes"]
                    file = BufferedInputFile(photo_bytes, filename="photo.jpg")
                    await callback.bot.send_photo(
                        chat_id=user.user_id,
                        photo=file,
                        caption=user_data["caption"],
                        parse_mode="HTML"
                    )
                else:
                    await callback.bot.send_message(
                        chat_id=user.user_id,
                        text=user_data["text"],
                        parse_mode="HTML"
                    )
                sent_count += 1
            except Exception as e:
                errors_count += 1
                print(f"Помилка розсилки для {user.user_id}: {e}")

        await callback.message.answer(
            f"Розсилку завершено!\n"
            f"✅ Успішно відправлено: {sent_count}\n"
            f"❌ Помилки: {errors_count}"
        )
        await state.clear()
    else:
        await callback.answer("У вас немає доступу.", show_alert=True)

@router.callback_query(F.data == "update_quote")
async def process_update_quote(callback: CallbackQuery, state: FSMContext):
    """Оновлення цитати для нагадувань"""
    if callback.from_user.id in ADMIN_IDS:
        await callback.answer()
        await callback.message.answer("Введіть нову цитату для щотижневих нагадувань:")
        await state.set_state(AdminStates.waiting_for_quote)
    else:
        await callback.answer("У вас немає доступу.", show_alert=True)

@router.message(AdminStates.waiting_for_quote)
async def process_new_quote(message: Message, state: FSMContext):
    """Збереження нової цитати"""
    if message.from_user.id in ADMIN_IDS:
        await update_quote(message.text)
        await message.answer(f"Цитату оновлено на:\n\n{message.text}")
        await state.clear()
    else:
        await message.answer("У вас немає доступу до цієї команди.")

def register_handlers(dp):
    dp.include_router(router)