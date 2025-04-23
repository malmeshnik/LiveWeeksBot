from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from utils.keyboards import get_main_menu_keyboard
from utils.states import IdeaStates
from database.db_operations import save_user_idea, is_admin
from config import ADMIN_IDS


router = Router()

@router.message(F.text == "💡 Запропонувати ідею")
async def suggest_idea(message: Message, state: FSMContext):
    """Запропонувати ідею для розвитку"""
    await message.answer(
        "Поділіться вашою ідеєю для покращення цього бота. "
        "Напишіть, що б ви хотіли додати або змінити."
    )
    await state.set_state(IdeaStates.waiting_for_idea)

@router.message(IdeaStates.waiting_for_idea)
async def process_idea(message: Message, state: FSMContext):
    """Обробка ідеї користувача"""
    user_id = message.from_user.id
    username = message.from_user.username or f"user_{user_id}"
    idea_text = message.text
    
    # Зберігаємо ідею в БД
    await save_user_idea(user_id, username, idea_text)
    
    # Відправляємо ідею всім адмінам
    for admin_id in ADMIN_IDS:
        try:
            await message.bot.send_message(
                chat_id=admin_id,
                text=f"📩 <b>Нова ідея від користувача</b>\n\n"
                     f"<b>Від:</b> @{username} (ID: {user_id})\n"
                     f"<b>Ідея:</b>\n{idea_text}"
            )
        except Exception as e:
            print(f"Помилка відправки ідеї адміну {admin_id}: {e}")
    
    await message.answer(
        "Дякуємо за вашу ідею! Ми обов'язково розглянемо її "
        "для подальшого розвитку бота.",
        reply_markup=get_main_menu_keyboard()
    )
    
    await state.clear()

def register_handlers(dp):
    dp.include_router(router)