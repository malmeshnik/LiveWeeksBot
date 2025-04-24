import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock

from datetime import datetime, timedelta
from scheduler.jobs import (
    setup_scheduler,
    add_scheduled_task,
    remove_scheduled_task,
    send_broadcast_message,
)

# Переважно твої імпорти будуть трохи інакшими — підстав `your_scheduler_module`

@pytest.fixture
def fake_bot():
    bot = AsyncMock()
    return bot

@pytest.mark.asyncio
async def test_setup_scheduler(fake_bot):
    scheduler = setup_scheduler(fake_bot)
    assert scheduler is not None
    job = scheduler.get_job('weekly_reminder')
    assert job is not None
    assert job.name == 'weekly_reminder'

@pytest.mark.asyncio
async def test_add_scheduled_task(fake_bot):
    send_time = datetime.now() + timedelta(seconds=5)
    scheduler = setup_scheduler(fake_bot)
    job_id = add_scheduled_task(fake_bot, "Hello test!", send_time)

    job = scheduler.get_job(job_id)
    assert job is not None
    assert job.func.__name__ == "send_broadcast_message"

def test_remove_scheduled_task(fake_bot):
    send_time = datetime.now() + timedelta(seconds=10)
    scheduler = setup_scheduler(fake_bot)
    job_id = add_scheduled_task(fake_bot, "Test remove", send_time)

    removed = remove_scheduled_task(job_id)
    assert removed is True

@pytest.mark.asyncio
async def test_send_broadcast_message(fake_bot, monkeypatch):
    fake_users = [MagicMock(user_id=111), MagicMock(user_id=222)]

    # Підміняємо get_all_active_users, щоб не тягнути з БД
    monkeypatch.setattr("scheduler.jobs.get_all_active_users", AsyncMock(return_value=fake_users))

    # Мокаєм send_message
    fake_bot.send_message = AsyncMock()

    await send_broadcast_message(fake_bot, "Test broadcast")

    assert fake_bot.send_message.call_count == len(fake_users)
    fake_bot.send_message.assert_any_call(chat_id=111, text="Test broadcast", parse_mode="HTML")
    fake_bot.send_message.assert_any_call(chat_id=222, text="Test broadcast", parse_mode="HTML")
