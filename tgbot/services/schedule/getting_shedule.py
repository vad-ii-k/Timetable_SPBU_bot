from datetime import date

from babel.dates import format_date

from tgbot.data_classes import StudyEvent, GroupEventsDay, EducatorEventsDay
from tgbot.misc.states import UserType
from tgbot.services.schedule.helpers import _get_monday_and_sunday_dates, _get_time_sticker, \
    _get_subject_format_sticker, _get_weekday_sticker
from tgbot.services.timetable_api.timetable_api import get_educator_schedule_from_tt, get_group_schedule_from_tt


async def get_schedule(tt_id: int, user_type: UserType) -> str:
    monday, sunday = _get_monday_and_sunday_dates()
    if user_type == UserType.STUDENT:
        schedule_from_timetable = await get_group_schedule_from_tt(tt_id, from_date=str(monday), to_date=str(sunday))
    else:
        schedule_from_timetable = await get_educator_schedule_from_tt(tt_id, from_date=str(monday), to_date=str(sunday))
    schedule = schedule_from_timetable.get_schedule_week_header()
    schedule = await schedule_week_body(schedule, schedule_from_timetable.events_days)
    return schedule


async def events_day_converter_to_msg(day: date, events: list[StudyEvent]) -> str:
    day_timetable = await schedule_weekday_header(format_date(day, "EEEE, d MMMM", locale="ru_RU"))
    for i, event in enumerate(events):
        if i == 0 or events[i-1] != event:
            day_timetable += (
                f'     ┈┈┈┈┈┈┈┈┈┈┈┈\n'
                f'    {"<s>" * event.is_canceled}<b>{event.subject_name}</b>{"</s>" * event.is_canceled}\n'
                f'    {_get_time_sticker(event.start_time.hour)} {event.start_time:%H:%M}-{event.end_time:%H:%M}\n'
                f'    <i>{_get_subject_format_sticker(event.subject_format)} {event.subject_format}</i>\n'
            )
        day_timetable += (
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
    weekday_sticker = _get_weekday_sticker(day_string)
    header = f"\n\n{weekday_sticker} <b>{day_string}</b>\n"
    return header
