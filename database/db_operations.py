import asyncio
from sqlalchemy import create_engine, func, select, update
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from datetime import datetime

from config import PATH_DB
from database.models import Base, User, UserIdea, AdminSettings

# Створюємо асинхронний двигун для бази даних
engine = create_async_engine(PATH_DB, echo=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def init_db():
    """Ініціалізація бази даних"""
    async with engine.begin() as conn:
        # Створюємо таблиці, якщо їх ще немає
        await conn.run_sync(Base.metadata.create_all)
        
        # Створюємо запис адмін-налаштувань, якщо його ще немає
        async with async_session() as session:
            admin_settings_count = await session.execute(
                select(func.count()).select_from(AdminSettings)
            )
            count = admin_settings_count.scalar()
            
            if count == 0:
                default_settings = AdminSettings(
                    quote_text="Час минає швидше, ніж ми думаємо..."
                )
                session.add(default_settings)
                await session.commit()

async def save_user(user_id, username, first_name, gender, birth_date):
    """Зберігає нового користувача або оновлює існуючого"""
    async with async_session() as session:
        # Перевіряємо, чи існує користувач
        result = await session.execute(
            select(User).where(User.user_id == user_id)
        )
        existing_user = result.scalars().first()
        
        if existing_user:
            # Оновлюємо дані існуючого користувача
            existing_user.username = username
            existing_user.first_name = first_name
            existing_user.gender = gender
            existing_user.birth_date = birth_date
            existing_user.is_active = True
        else:
            # Створюємо нового користувача
            new_user = User(
                user_id=user_id,
                username=username,
                first_name=first_name,
                gender=gender,
                birth_date=birth_date,
                registration_date=datetime.now().date(),
                notifications_enabled=True,
                is_active=True
            )
            session.add(new_user)
            
        await session.commit()

async def get_user(user_id):
    """Отримує дані користувача з БД"""
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.user_id == user_id)
        )
        return result.scalars().first()

async def update_user_gender(user_id, gender):
    """Оновлює стать користувача"""
    async with async_session() as session:
        await session.execute(
            update(User)
            .where(User.user_id == user_id)
            .values(gender=gender)
        )
        await session.commit()

async def update_user_birth_date(user_id, birth_date):
    """Оновлює дату народження користувача"""
    async with async_session() as session:
        await session.execute(
            update(User)
            .where(User.user_id == user_id)
            .values(birth_date=birth_date)
        )
        await session.commit()

async def delete_user_data(user_id):
    """Видаляє всі дані користувача (встановлює неактивним)"""
    async with async_session() as session:
        await session.execute(
            update(User)
            .where(User.user_id == user_id)
            .values(is_active=False)
        )
        await session.commit()

async def toggle_notifications(user_id, enabled):
    """Увімкнути/вимкнути нагадування для користувача"""
    async with async_session() as session:
        await session.execute(
            update(User)
            .where(User.user_id == user_id)
            .values(notifications_enabled=enabled)
        )
        await session.commit()

async def save_user_idea(user_id, username, idea_text):
    """Зберігає пропозицію користувача"""
    async with async_session() as session:
        new_idea = UserIdea(
            user_id=user_id,
            username=username,
            idea_text=idea_text,
            created_at=datetime.now().date()
        )
        session.add(new_idea)
        await session.commit()

async def get_all_active_users():
    """Отримує список всіх активних користувачів"""
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.is_active == True)
        )
        return result.scalars().all()

async def get_admin_settings():
    """Отримує налаштування адміна (цитату)"""
    async with async_session() as session:
        result = await session.execute(
            select(AdminSettings).order_by(AdminSettings.id.desc()).limit(1)
        )
        return result.scalars().first()
    
async def get_user_birth(user_id):
    """Отримує дату народження користувача"""
    async with async_session() as session:
        result = await session.execute(
            select(User.birth_date).where(User.id == user_id)
        )
        birth_date = result.scalar_one_or_none()
        return birth_date

async def update_quote(new_quote):
    """Оновлює цитату для нагадувань"""
    async with async_session() as session:
        settings = await get_admin_settings()
        if settings:
            settings.quote_text = new_quote
            await session.commit()
        else:
            new_settings = AdminSettings(quote_text=new_quote)
            session.add(new_settings)
            await session.commit()

async def get_stats():
    """Отримує статистику про користувачів"""
    async with async_session() as session:
        # Загальна кількість користувачів
        total_users_result = await session.execute(
            select(func.count()).select_from(User).where(User.is_active == True)
        )
        total_users = total_users_result.scalar()
        
        # Кількість чоловіків
        male_count_result = await session.execute(
            select(func.count()).select_from(User)
            .where(User.is_active == True)
            .where(User.gender == 'Чоловік')
        )
        male_count = male_count_result.scalar()
        
        # Кількість жінок
        female_count_result = await session.execute(
            select(func.count()).select_from(User)
            .where(User.is_active == True)
            .where(User.gender == 'Жінка')
        )
        female_count = female_count_result.scalar()
        
        # Середній вік
        today = datetime.now().date()
        users = await get_all_active_users()
        
        if users:
            total_age = sum((today - user.birth_date).days / 365.25 for user in users)
            avg_age = total_age / len(users)
        else:
            avg_age = 0
        
        return {
            'total_users': total_users,
            'active_users': total_users,
            'male_count': male_count,
            'female_count': female_count,
            'avg_age': avg_age
        }

def is_admin(user_id):
    """Перевіряє, чи є користувач адміністратором"""
    from config import ADMIN_IDS
    return user_id in ADMIN_IDS