from datetime import date, timedelta

from aiogram.utils.i18n import gettext as _
from aiogram.types import BufferedInputFile

from tgbot.data_classes import GroupEventsDay, EducatorEventsDay
from tgbot.misc.states import UserType
from tgbot.services.image_converter import image_to_buffered_input_file
from tgbot.services.schedule.helpers import _get_monday_and_sunday_dates, get_schedule_weekday_header
from tgbot.services.timetable_api.timetable_api import get_educator_schedule_from_tt, get_group_schedule_from_tt


async def get_text_week_schedule(tt_id: int, user_type: UserType, week_counter: int) -> tuple[str, str]:
    monday, sunday = _get_monday_and_sunday_dates(week_counter=week_counter)
    if user_type == UserType.STUDENT:
        schedule_from_timetable = await get_group_schedule_from_tt(tt_id, from_date=str(monday), to_date=str(sunday))
    else:
        schedule_from_timetable = await get_educator_schedule_from_tt(tt_id, from_date=str(monday), to_date=str(sunday))
    schedule = await schedule_from_timetable.get_schedule_week_header()
    schedule = await schedule_week_body(schedule, schedule_from_timetable.events_days)
    return schedule, schedule_from_timetable.name


async def get_text_day_schedule(tt_id: int, user_type: UserType, day_counter: int) -> str:
    monday, sunday = _get_monday_and_sunday_dates(day_counter=day_counter)
    if user_type == UserType.STUDENT:
        schedule_from_timetable = await get_group_schedule_from_tt(tt_id, from_date=str(monday), to_date=str(sunday))
    else:
        schedule_from_timetable = await get_educator_schedule_from_tt(tt_id, from_date=str(monday), to_date=str(sunday))
    schedule = await schedule_from_timetable.get_schedule_week_header()
    schedule = await schedule_day_body(schedule, schedule_from_timetable.events_days, day_counter)
    return schedule


async def get_image_schedule(tt_id: int, user_type: UserType, week_counter: int) -> tuple[str, BufferedInputFile]:
    monday, sunday = _get_monday_and_sunday_dates(week_counter=week_counter)
    if user_type == UserType.STUDENT:
        schedule_from_timetable = await get_group_schedule_from_tt(tt_id, from_date=str(monday), to_date=str(sunday))
    else:
        schedule_from_timetable = await get_educator_schedule_from_tt(tt_id, from_date=str(monday), to_date=str(sunday))
    schedule = await schedule_from_timetable.get_schedule_week_header()
    photo = await image_to_buffered_input_file(schedule_from_timetable)
    return schedule, photo


async def schedule_week_body(schedule: str, events_days: list[GroupEventsDay | EducatorEventsDay]) -> str:
    if len(events_days) > 0:
        for event_day in events_days:
            day_schedule = await event_day.events_day_converter_to_msg()
            if len(schedule) + len(day_schedule) <= 4060:
                schedule += day_schedule
            else:
                schedule += _("\n\n📛 Сообщение слишком длинное...")
                break
    else:
        schedule += _("\n🏖 Занятий на этой неделе нет")
    return schedule


async def schedule_day_body(
        schedule: str, events_days: list[GroupEventsDay | EducatorEventsDay], day_counter: int
) -> str:
    day = date.today() + timedelta(day_counter)
    day_schedule = ""
    for event_day in events_days:
        if event_day.day == day:
            day_schedule += await event_day.events_day_converter_to_msg()
            if len(schedule) + len(day_schedule) <= 4060:
                schedule += day_schedule
            else:
                schedule += _("\n\n📛 Сообщение слишком длинное...")
                break
    if day_schedule == "":
        schedule += await get_schedule_weekday_header(day)
        schedule += _("🏖 Занятий в этот день нет")
    return schedule
