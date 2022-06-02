import datetime

import pytz

from tgbot.handlers.users.helpers import create_answer_based_on_content
from tgbot.loader import db, bot
from utils.timetable.get_timetable import get_timetable


async def job_send_daily_summary() -> None:
    current_hour = datetime.datetime.now(pytz.timezone('Europe/Moscow')).hour
    students, teachers = await db.get_users_with_sign_to_summary(datetime.time(current_hour))
    for tg_id, tt_id in students:
        await send_daily_summary('student', tg_id, tt_id, day_counter=1 * (current_hour > 12))
    for tg_id, tt_id in teachers:
        await send_daily_summary('teacher', tg_id, tt_id, day_counter=1 * (current_hour > 12))


async def send_daily_summary(user_type: str, tg_id: int, tt_id: int, day_counter: int) -> None:
    user_db = await db.get_user_by_tg_id(tg_id)
    settings = await db.get_settings(user_db)
    is_picture: bool = settings.schedule_view_is_picture
    text = f"🔔 Расписание на {'завтра' if day_counter == 1 else 'сегодня'}\n"
    message = await bot.send_message(tg_id, text)
    text += await get_timetable(
        tt_id=tt_id, is_picture=is_picture, user_type=user_type, day_counter=day_counter
    )
    await create_answer_based_on_content(message, text, is_picture)
