from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from datetime import datetime, timedelta

from utils.notifications import send_notifications_to_all
from database.db_operations import get_all_active_users

# Ініціалізуємо глобальний планувальник
scheduler = None

def setup_scheduler(bot):
    """Налаштовує планувальник завдань"""
    global scheduler
    
    # Створюємо планувальник, якщо його ще немає
    if scheduler is None:
        scheduler = AsyncIOScheduler()
        jobstore = MemoryJobStore()
        scheduler.add_jobstore(jobstore, alias='default')
        
        # Додаємо щотижневе нагадування (кожної неділі о 12:00)
        scheduler.add_job(
            weekly_reminder,
            'cron',
            day_of_week='sun',
            hour=12,
            minute=0,
            kwargs={'bot': bot},
            id='weekly_reminder',
            replace_existing=True
        )

        # run_time = datetime.now() + timedelta(minutes=5)

        # scheduler.add_job(
        #     weekly_reminder,
        #     'cron',
        #     day_of_week=run_time.strftime('%a').lower(),  # або просто '*' для будь-якого дня
        #     hour=run_time.hour,
        #     minute=run_time.minute,
        #     kwargs={'bot': bot},
        #     id='test_weekly_reminder',
        #     replace_existing=True
        # )
    
    return scheduler

async def weekly_reminder(bot):
    """Щотижневе нагадування для всіх користувачів"""
    success_count, failed_count = await send_notifications_to_all(bot)
    print(f"Щотижневі нагадування: успішно - {success_count}, невдачі - {failed_count}")

def add_scheduled_task(bot, text, send_time):
    """Додає заплановану розсилку"""
    global scheduler
    
    if scheduler is None:
        scheduler = setup_scheduler(bot)
    
    # Створюємо унікальний ID для завдання
    job_id = f"broadcast_{datetime.now().timestamp()}"
    
    # Додаємо завдання в планувальник
    scheduler.add_job(
        send_broadcast_message,
        'date',
        run_date=send_time,
        kwargs={'bot': bot, 'text': text},
        id=job_id
    )
    
    return job_id

def remove_scheduled_task(job_id):
    """Видаляє заплановану розсилку"""
    global scheduler
    
    try:
        scheduler.remove_job(job_id)
        return True
    except Exception as e:
        print(f"Помилка видалення завдання {job_id}: {e}")
        return False

async def send_broadcast_message(bot, text):
    """Відправляє заплановане повідомлення всім користувачам"""
    users = await get_all_active_users()
    
    success_count = 0
    failed_count = 0
    
    for user in users:
        try:
            await bot.send_message(
                chat_id=user.user_id,
                text=text,
                parse_mode="HTML"
            )
            success_count += 1
        except Exception as e:
            failed_count += 1
            print(f"Помилка відправки розсилки користувачу {user.user_id}: {e}")
    
    print(f"Розсилка завершена: успішно - {success_count}, невдачі - {failed_count}")