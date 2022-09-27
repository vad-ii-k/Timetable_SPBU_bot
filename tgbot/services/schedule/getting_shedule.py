import json
from datetime import date, time
from typing import Final

from babel.dates import format_date

from tgbot.misc.states import UserType
from tgbot.services.schedule.helpers import _get_monday_and_sunday_dates
from tgbot.services.timetable_api.timetable_api import get_schedule_from_tt
from pydantic import BaseModel, Field, validator


class StudyEvent(BaseModel):
    start_time: time = Field(alias="Start")
    end_time: time = Field(alias="End")
    subject: str = Field(alias="Subject")
    location: str = Field(alias="LocationsDisplayText")
    is_canceled: bool = Field(alias="IsCancelled")
    groups: str = Field(alias="ContingentUnitName")

    @validator('start_time', 'end_time', pre=True)
    def from_datetime_to_time(cls, v):
        return v.split('T')[1]


class EducatorEventsDay(BaseModel):
    day: date = Field(alias="Day")
    study_events: list[StudyEvent] = Field(alias="DayStudyEvents")

    @validator('day', pre=True)
    def from_datetime_to_date(cls, v):
        return v.split('T')[0]


class EducatorSchedule(BaseModel):
    educator_tt_id: int = Field(alias="EducatorMasterId")
    full_name: str = Field(alias="EducatorLongDisplayText")
    events_days: list[EducatorEventsDay] = Field(alias="EducatorEventsDays")


async def get_schedule(tt_id: int, user_type: UserType) -> str:
    monday, sunday = await _get_monday_and_sunday_dates()
    response = await get_schedule_from_tt(tt_id=tt_id, user_type=user_type, from_date=str(monday), to_date=str(sunday))
    info = EducatorSchedule.parse_raw(json.dumps(response))
    schedule = await educator_schedule_week_header(tt_id, info.full_name, monday, sunday)
    if len(info.events_days) > 0:
        for day in info.events_days:
            day_schedule = await events_day_converter_to_msg(day=day.day)
            if len(schedule) + len(day_schedule) < 4060:
                schedule += day_schedule
            else:
                schedule += "\n\n📛 Сообщение слишком длинное..."
                break
    return schedule


TT_URL: Final[str] = "https://timetable.spbu.ru/"


async def events_day_converter_to_msg(day: date) -> str:
    day_timetable = await schedule_day_header(format_date(day, "EEEE, d MMMM", locale="ru_RU"))
    return day_timetable


async def educator_schedule_week_header(educator_id: int, educator_fullname: str, monday: date, sunday: date) -> str:
    header = (
        f"🧑‍🏫 Преподаватель: <b>{educator_fullname}</b>\n"
        f"📆 Неделя: <a href='{TT_URL}WeekEducatorEvents/{educator_id}/{monday}'>{monday:%d.%m} — {sunday:%d.%m}</a>\n"
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


async def schedule_day_header(day_string: str) -> str:
    weekday_sticker = await get_weekday_sticker(day_string)
    header = f"\n\n{weekday_sticker} <b>{day_string}</b>\n"
    return header
