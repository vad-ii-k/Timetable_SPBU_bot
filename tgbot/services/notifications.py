import logging
from datetime import datetime, time

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from tgbot.config import bot
from tgbot.misc.states import UserType
from tgbot.services.db_api.db_commands import database
from tgbot.services.schedule.getting_shedule import get_text_day_schedule, get_image_day_schedule


async def send_daily_summary(tg_id: int, user_type: UserType, tt_id: int, day_counter: int) -> None:
    settings = await database.get_settings_by_tg_id(tg_id)
    is_picture: bool = settings.schedule_view_is_picture
    header = f"🔔 Расписание на {'завтра' if day_counter == 1 else 'сегодня'}\n"
    if is_picture:
        schedule_text, photo = await get_image_day_schedule(tt_id, user_type, day_counter=day_counter)
        await bot.send_photo(chat_id=tg_id, photo=photo, caption=header + schedule_text)
    else:
        schedule_text = await get_text_day_schedule(tt_id, user_type, day_counter=day_counter)
        await bot.send_message(chat_id=tg_id, text=header + schedule_text)


async def job_send_daily_summary():
    current_hour = datetime.now().hour
    user_with_main_schedule = await database.get_users_with_sign_to_summary(time(current_hour))
    logging.info(user_with_main_schedule)
    day_counter = 1 * (current_hour > 12)
    for tg_id, user_type, tt_id in user_with_main_schedule:
        await send_daily_summary(tg_id, user_type, tt_id, day_counter)


async def start_scheduler(scheduler: AsyncIOScheduler):
    scheduler.add_job(job_send_daily_summary, "cron", hour="7-9, 19-21")
    scheduler.start()
