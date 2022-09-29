from datetime import date
from typing import Final

from babel.dates import format_date

from tgbot.data_classes import StudyEvent, GroupEventsDay, EducatorEventsDay
from tgbot.services.schedule.helpers import _get_monday_and_sunday_dates
from tgbot.services.timetable_api.timetable_api import get_educator_schedule_from_tt, get_group_schedule_from_tt


async def get_educator_schedule(tt_id: int) -> str:
    monday, sunday = await _get_monday_and_sunday_dates()
    educator_schedule = await get_educator_schedule_from_tt(tt_id=tt_id, from_date=str(monday), to_date=str(sunday))
    schedule = await educator_schedule_week_header(tt_id, educator_schedule.full_name, monday, sunday)
    schedule = await schedule_week_body(schedule, educator_schedule.events_days)
    return schedule


async def get_group_schedule(tt_id: int) -> str:
    monday, sunday = await _get_monday_and_sunday_dates()
    group_schedule = await get_group_schedule_from_tt(tt_id=tt_id, from_date=str(monday), to_date=str(sunday))
    schedule = await group_schedule_week_header(tt_id, group_schedule.group_name, monday, sunday)
    schedule = await schedule_week_body(schedule, group_schedule.events_days)
    return schedule


TT_URL: Final[str] = "https://timetable.spbu.ru/"


async def events_day_converter_to_msg(day: date, events: list[StudyEvent]) -> str:
    day_timetable = await schedule_weekday_header(format_date(day, "EEEE, d MMMM", locale="ru_RU"))
    for event in events:
        day_timetable += (
            f'     ┈┈┈┈┈┈┈┈┈┈┈┈\n'
            f'    {"<s>" * event.is_canceled}<b>{event.subject_name}</b>{"</s>" * event.is_canceled}\n'
            f'    <u>🕟 {event.start_time:%H:%M}-{event.end_time:%H:%M}</u>\n'
            f'    <i>✍🏻 {event.subject_format}</i>\n'
            f"    <i>{event.get_contingent(with_sticker=True)}</i>\n"
            f"    <i>🚩 {event.location}</i>\n"
        )
    return day_timetable


async def schedule_week_body(schedule: str, events_days: list[GroupEventsDay | EducatorEventsDay]) -> str:
    if len(events_days) > 0:
        for day in events_days:
            day_schedule = await events_day_converter_to_msg(day=day.day, events=day.study_events)
            if len(schedule) + len(day_schedule) <= 4060:
                schedule += day_schedule
            else:
                schedule += "\n\n📛 Сообщение слишком длинное..."
                break
    else:
        schedule += "\n🏖 Занятий на этой неделе нет"
    return schedule


async def educator_schedule_week_header(educator_id: int, educator_fullname: str, monday: date, sunday: date) -> str:
    header = (
        f"🧑‍🏫 Преподаватель: <b>{educator_fullname}</b>\n"
        f"📆 Неделя: <a href='{TT_URL}WeekEducatorEvents/{educator_id}/{monday}'>"
        f"{monday:%d.%m} — {sunday:%d.%m}</a>\n"
    )
    return header


async def group_schedule_week_header(group_id: int, group_name: str, monday: date, sunday: date) -> str:
    header = (
        f"👨‍👩‍👧‍👦 Группа: <b>{group_name}</b>\n"
        f"📆 Неделя: <a href='{TT_URL}MATH/StudentGroupEvents/Primary/{group_id}/{monday}'>"
        f"{monday:%d.%m} — {sunday:%d.%m}</a>\n"
    )
    return header


async def get_weekday_sticker(day: str) -> str:
    weekday_sticker = ""
    match day.split(",")[0]:
        case "понедельник" | "Monday":
            weekday_sticker = "1️⃣"
        case "вторник" | "Tuesday":
            weekday_sticker = "2️⃣"
        case "среда" | "Wednesday":
            weekday_sticker = "3️⃣"
        case "четверг" | "Thursday":
            weekday_sticker = "4️⃣"
        case "пятница" | "Friday":
            weekday_sticker = "5️⃣"
        case "суббота" | "Saturday":
            weekday_sticker = "6️⃣"
        case "воскресенье" | "Sunday":
            weekday_sticker = "7️⃣"
    return weekday_sticker


async def schedule_weekday_header(day_string: str) -> str:
    weekday_sticker = await get_weekday_sticker(day_string)
    header = f"\n\n{weekday_sticker} <b>{day_string}</b>\n"
    return header
