""" Functions for getting a schedule """

from datetime import date, timedelta

from aiogram.types import BufferedInputFile
from aiogram.utils.i18n import gettext as _

from tgbot.services.image_converter import get_rendered_image
from tgbot.services.schedule.class_schedule import EducatorSchedule, EventsDay, GroupSchedule, Schedule
from tgbot.services.schedule.data_classes import UserType
from tgbot.services.schedule.helpers import get_monday_and_sunday_dates, get_schedule_weekday_header
from tgbot.services.timetable_api.timetable_api import get_educator_schedule_from_tt, get_group_schedule_from_tt


async def get_schedule_from_tt_depending_on_user_type(
    tt_id: int, user_type: UserType, monday: date, sunday: date
) -> GroupSchedule | EducatorSchedule:
    """

    :param tt_id:
    :param user_type:
    :param monday:
    :param sunday:
    :return:
    """
    if user_type == UserType.STUDENT:
        schedule_from_timetable = await get_group_schedule_from_tt(tt_id, from_date=str(monday), to_date=str(sunday))
    else:
        schedule_from_timetable = await get_educator_schedule_from_tt(tt_id, from_date=str(monday), to_date=str(sunday))
    return schedule_from_timetable.model_copy(deep=True)


async def get_text_week_schedule(tt_id: int, user_type: UserType, week_counter: int) -> tuple[str, str]:
    """

    :param tt_id:
    :param user_type:
    :param week_counter:
    :return:
    """
    monday, sunday = get_monday_and_sunday_dates(week_counter=week_counter)
    schedule_from_timetable = await get_schedule_from_tt_depending_on_user_type(tt_id, user_type, monday, sunday)
    schedule = await schedule_from_timetable.get_schedule_week_header()
    schedule = await schedule_week_body(schedule, schedule_from_timetable.events_days)
    return schedule, schedule_from_timetable.name


async def get_text_day_schedule(tt_id: int, user_type: UserType, day_counter: int) -> str:
    """

    :param tt_id:
    :param user_type:
    :param day_counter:
    :return:
    """
    monday, sunday = get_monday_and_sunday_dates(day_counter=day_counter)
    schedule_from_timetable = await get_schedule_from_tt_depending_on_user_type(tt_id, user_type, monday, sunday)
    schedule = await schedule_from_timetable.get_schedule_week_header()
    schedule = await schedule_day_body(schedule, schedule_from_timetable.events_days, day_counter)
    return schedule


async def get_image_week_schedule(tt_id: int, user_type: UserType, week_counter: int) -> tuple[str, BufferedInputFile]:
    """

    :param tt_id:
    :param user_type:
    :param week_counter:
    :return:
    """
    monday, sunday = get_monday_and_sunday_dates(week_counter=week_counter)
    schedule_from_timetable = await get_schedule_from_tt_depending_on_user_type(tt_id, user_type, monday, sunday)
    schedule = await schedule_from_timetable.get_schedule_week_header()
    photo = await get_rendered_image(schedule_from_timetable, schedule_type="week")
    return schedule, photo


async def get_image_day_schedule(tt_id: int, user_type: UserType, day_counter: int) -> tuple[str, BufferedInputFile]:
    """

    :param tt_id:
    :param user_type:
    :param day_counter:
    :return:
    """
    monday, sunday = get_monday_and_sunday_dates(day_counter=day_counter)
    schedule_from_timetable = await get_schedule_from_tt_depending_on_user_type(tt_id, user_type, monday, sunday)
    schedule = await schedule_from_timetable.get_schedule_week_header()
    schedule += await _transforming_schedule_for_image_for_day(schedule_from_timetable, day_counter)
    photo = await get_rendered_image(schedule_from_timetable, schedule_type="day")
    return schedule, photo


async def schedule_week_body(schedule: str, events_days: list[EventsDay]) -> str:
    """

    :param schedule:
    :param events_days:
    :return:
    """
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


async def schedule_day_body(schedule: str, events_days: list[EventsDay], day_counter: int) -> str:
    """

    :param schedule:
    :param events_days:
    :param day_counter:
    :return:
    """
    day = date.today() + timedelta(day_counter)
    day_schedule = ""
    for event_day in events_days:
        if event_day.day == day:
            day_schedule += await event_day.events_day_converter_to_msg()
            if len(schedule) + len(day_schedule) <= 4060:
                schedule += day_schedule
            else:
                try:
                    schedule += _("\n\n📛 Сообщение слишком длинное...")
                except LookupError:
                    schedule += "\n\n📛 Сообщение слишком длинное..."
                break
    if day_schedule == "":
        schedule += "\n\n" + await get_schedule_weekday_header(day)
        try:
            schedule += _("🏖 Занятий в этот день нет")
        except LookupError:
            schedule += "🏖 Занятий в этот день нет"
    return schedule


async def _transforming_schedule_for_image_for_day(schedule_from_timetable: Schedule, day_counter: int) -> str:
    """

    :param schedule_from_timetable:
    :param day_counter:
    :return:
    """
    day = date.today() + timedelta(day_counter)
    schedule = await get_schedule_weekday_header(day)
    for index, event_day in enumerate(schedule_from_timetable.events_days):
        if event_day.day == day:
            schedule_from_timetable.events_days = schedule_from_timetable.events_days[index : index + 1]
    if len(schedule_from_timetable.events_days) > 1:
        schedule_from_timetable.events_days.clear()
        schedule_from_timetable.day = day
    return schedule
