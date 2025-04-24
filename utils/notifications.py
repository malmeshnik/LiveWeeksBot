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

        # Прожиті роки
        years = total_days // 365

        # Залишок днів після повних років
        days_after_years = total_days % 365

        # Прожиті тижні після повних років
        weeks = days_after_years // 7

        # І залишок днів після повних тижнів
        days = days_after_years % 7

        # Загальна кількість прожитих тижнів (окремо, якщо треба)
        total_weeks = total_days // 7

        # Загальна кількість днів життя (залежно від статі)
        total_life_days = 72 * 365 if user.gender == 'Жінка' else 66 * 365
        days_left = max(0, total_life_days - total_days)

        # Скільки років і тижнів залишилося
        years_left = days_left // 365
        weeks_left = (days_left % 365) // 7
        days = (days_left % 365) % 7

        lived_text = "прожила" if user.gender == 'Жінка' else "прожив"

        text = f'''{user.first_name}, ти {lived_text} свій 1270-й тиждень!
Тобі: {years} років, {weeks} днів
Жити залишилося всього {years_left} років {weeks_left} тижнів та {days} днів!

Час минає швидше, ніж ми думаємо...'''
        
        # Формуємо та відправляємо повідомлення
        await bot.send_photo(
            chat_id=user.user_id,
            photo=open(table_image, 'rb'),
            caption=text
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