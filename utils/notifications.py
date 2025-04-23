from datetime import datetime, timedelta

from database.db_operations import get_all_active_users, get_admin_settings
from utils.image_generator import generate_life_table

async def send_notification(bot, user):
    """Відправляє нагадування користувачу"""
    try:
        # Отримуємо цитату з адмін-налаштувань
        admin_settings = await get_admin_settings()
        quote = admin_settings.quote_text
        
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
        
        # Формуємо та відправляємо повідомлення
        await bot.send_photo(
            chat_id=user.user_id,
            photo=open(table_image, 'rb'),
            caption=f"{user.first_name}, ти прожив(ла) свій {lived_weeks}-й тиждень!\n"
                    f"Тобі: {years} років, {remaining_days} днів\n"
                    f"Жити залишилося всього {days_left} днів!\n\n"
                    f"{quote}"
        )
        
        return True
    except Exception as e:
        print(f"Помилка відправки нагадування користувачу {user.user_id}: {e}")
        return False

async def send_notifications_to_all(bot):
    """Відправляє нагадування всім активним користувачам"""
    users = await get_all_active_users()
    
    success_count = 0
    failed_count = 0
    
    for user in users:
        if user.notifications_enabled:
            success = await send_notification(bot, user)
            if success:
                success_count += 1
            else:
                failed_count += 1
    
    return success_count, failed_count

async def schedule_broadcast(bot, text, send_time):
    """Планує розсилку на певний час"""
    from scheduler.jobs import add_scheduled_task
    
    # Зберігаємо завдання у планувальнику
    job_id = add_scheduled_task(bot, text, send_time)
    
    return job_id

async def cancel_scheduled_broadcast(job_id):
    """Скасовує заплановану розсилку"""
    from scheduler.jobs import remove_scheduled_task
    
    success = remove_scheduled_task(job_id)
    return success