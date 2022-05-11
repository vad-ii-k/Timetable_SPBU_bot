from datetime import timedelta, date
from typing import Tuple

from utils.db_api.db_timetable import StudyEvent


async def calculator_of_days(day_counter: int) -> Tuple[date, date]:
    if day_counter > 0:
        current_date = date.today() + timedelta(day_counter)
    else:
        current_date = date.today() - timedelta(-day_counter)
    next_day = current_date + timedelta(days=1)
    return current_date, next_day


async def calculator_of_week_days(week_counter: int) -> Tuple[date, date]:
    current_date = date.today() + timedelta(week_counter * 7)
    monday = current_date - timedelta(days=current_date.weekday())
    sunday = monday + timedelta(days=6)
    return monday, sunday


async def get_weekday_sticker(day: str) -> str:
    weekday_sticker = ''
    match day.split(",")[0]:
        case 'понедельник' | 'Monday':
            weekday_sticker = '1️⃣'
        case 'вторник' | 'Tuesday':
            weekday_sticker = '2️⃣'
        case 'среда' | 'Wednesday':
            weekday_sticker = '3️⃣'
        case 'четверг' | 'Thursday':
            weekday_sticker = '4️⃣'
        case 'пятница' | 'Friday':
            weekday_sticker = '5️⃣'
        case 'суббота' | 'Saturday':
            weekday_sticker = '6️⃣'
        case 'воскресенье' | 'Sunday':
            weekday_sticker = '7️⃣'
    return weekday_sticker


def is_basic_events_info_identical(event1: StudyEvent, event2: StudyEvent) -> bool:
    return event1.subject_name != event2.subject_name \
        or event1.start_time != event2.start_time or event1.end_time != event2.end_time \
        or event1.subject_format != event2.subject_format or event1.is_canceled != event2.is_canceled
