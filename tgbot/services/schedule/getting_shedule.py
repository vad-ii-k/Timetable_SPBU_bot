from aiogram.utils.i18n import gettext as _

from tgbot.data_classes import GroupEventsDay, EducatorEventsDay
from tgbot.misc.states import UserType
from tgbot.services.schedule.helpers import _get_monday_and_sunday_dates
from tgbot.services.timetable_api.timetable_api import get_educator_schedule_from_tt, get_group_schedule_from_tt


async def get_schedule(tt_id: int, user_type: UserType, week_counter: int = 0) -> tuple[str, str]:
    monday, sunday = _get_monday_and_sunday_dates(week_counter)
    if user_type == UserType.STUDENT:
        schedule_from_timetable = await get_group_schedule_from_tt(tt_id, from_date=str(monday), to_date=str(sunday))
    else:
        schedule_from_timetable = await get_educator_schedule_from_tt(tt_id, from_date=str(monday), to_date=str(sunday))
    schedule = await schedule_from_timetable.get_schedule_week_header()
    schedule = await schedule_week_body(schedule, schedule_from_timetable.events_days)
    return schedule, schedule_from_timetable.name


async def schedule_week_body(schedule: str, events_days: list[GroupEventsDay | EducatorEventsDay]) -> str:
    if len(events_days) > 0:
        for day in events_days:
            day_schedule = await day.events_day_converter_to_msg()
            if len(schedule) + len(day_schedule) <= 4060:
                schedule += day_schedule
            else:
                schedule += _("\n\n📛 Сообщение слишком длинное...")
                break
    else:
        schedule += _("\n🏖 Занятий на этой неделе нет")
    return schedule[:4096]
