import asyncio
import logging
from aiogram import Bot, Dispatcher, Router
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties

from config import BOT_TOKEN
from handlers import start, profile, ideas, admin
from database.db_operations import init_db
from scheduler.jobs import setup_scheduler

async def main():
    # Налаштування логування
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Ініціалізація бота та диспетчера
    bot = Bot(
            token=BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Ініціалізація бази даних
    await init_db()
    
    # Реєстрація хендлерів
    start.register_handlers(dp)
    profile.register_handlers(dp)
    ideas.register_handlers(dp)
    admin.register_handlers(dp)
    
    # Запуск планувальника завдань
    scheduler = setup_scheduler(bot)
    scheduler.start()
    
    await bot.delete_webhook(drop_pending_updates=True)
    
    # Запуск поллінгу
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())