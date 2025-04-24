import os
from dotenv import load_dotenv

# Завантаження змінних оточення з .env файлу
load_dotenv('.env', override=True)

# Токен бота
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Налаштування бази даних
db_file = os.getenv("PATH_DB")
# Формуємо правильний URI для SQLAlchemy
PATH_DB = f"sqlite+aiosqlite:///{db_file}"

# ID адміністраторів
ADMIN_IDS = [int(id) for id in os.getenv("ADMIN_IDS", "").split(",") if id]
