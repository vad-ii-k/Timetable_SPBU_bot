from datetime import date

from babel.dates import format_date

from tgbot.data_classes import StudyEvent, GroupEventsDay, EducatorEventsDay
from tgbot.misc.states import UserType
from tgbot.services.schedule.helpers import _get_monday_and_sunday_dates
from tgbot.services.timetable_api.timetable_api import get_educator_schedule_from_tt, get_group_schedule_from_tt


async def get_schedule(tt_id: int, user_type: UserType) -> str:
    monday, sunday = await _get_monday_and_sunday_dates()
    if user_type == UserType.STUDENT:
        schedule_from_timetable = await get_group_schedule_from_tt(tt_id, from_date=str(monday), to_date=str(sunday))
    else:
        schedule_from_timetable = await get_educator_schedule_from_tt(tt_id, from_date=str(monday), to_date=str(sunday))
    schedule = schedule_from_timetable.get_schedule_week_header()
    schedule = await schedule_week_body(schedule, schedule_from_timetable.events_days)
    return schedule


async def events_day_converter_to_msg(day: date, events: list[StudyEvent]) -> str:
    day_timetable = await schedule_weekday_header(format_date(day, "EEEE, d MMMM", locale="ru_RU"))
    for event in events:
        day_timetable += (
            f'     ┈┈┈┈┈┈┈┈┈┈┈┈\n'
            f'    {"<s>" * event.is_canceled}<b>{event.subject_name}</b>{"</s>" * event.is_canceled}\n'
            f'    {await get_time_sticker(event.start_time.hour)} {event.start_time:%H:%M}-{event.end_time:%H:%M}\n'
            f'    <i>{await get_subject_format_sticker(event.subject_format)} {event.subject_format}</i>\n'
            f"    <i>{event.get_contingent(with_sticker=True)}</i>\n"
            f"    <i>📍 {event.location}</i>\n"
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


async def schedule_weekday_header(day_string: str) -> str:
    weekday_sticker = await get_weekday_sticker(day_string)
    header = f"\n\n{weekday_sticker} <b>{day_string}</b>\n"
    return header


async def get_time_sticker(hour: int) -> str:
    time_sticker = ""
    match hour:
        case 0 | 12:
            time_sticker = "🕛"
        case 1 | 13:
            time_sticker = "🕐"
        case 2 | 14:
            time_sticker = "🕑"
        case 3 | 15:
            time_sticker = "🕒"
        case 4 | 16:
            time_sticker = "🕓"
        case 5 | 17:
            time_sticker = "🕔"
        case 6 | 18:
            time_sticker = "🕕"
        case 7 | 19:
            time_sticker = "🕖"
        case 8 | 20:
            time_sticker = "🕗"
        case 9 | 21:
            time_sticker = "🕘"
        case 10 | 22:
            time_sticker = "🕙"
        case 11 | 23:
            time_sticker = "🕚"
    return time_sticker


async def get_subject_format_sticker(subject_format: str) -> str:
    format_sticker = "✍🏼"
    match subject_format.split(" ")[0]:
        case "лекция":
            format_sticker = "🗣"
        case "практическое":
            format_sticker = "🧑🏻‍💻"
        case "лабораторная":
            format_sticker = "🔬"
        case "семинар":
            format_sticker = "💬"
        case "консультация":
            format_sticker = "🤝🏼"
        case "экзамен":
            format_sticker = "❗"
        case "зачёт":
            format_sticker = "⚠️"
    return format_sticker


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
