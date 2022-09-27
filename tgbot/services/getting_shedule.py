import json
from datetime import date, time

from tgbot.misc.states import UserType
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
    tt_id: int = Field(alias="EducatorMasterId")
    full_name: str = Field(alias="EducatorLongDisplayText")
    events_days: list[EducatorEventsDay] = Field(alias="EducatorEventsDays")


async def get_schedule(tt_id: int, user_type: UserType) -> str:
    response = await get_schedule_from_tt(tt_id=tt_id, user_type=user_type)
    if user_type == UserType.EDUCATOR:
        info = EducatorSchedule.parse_raw(json.dumps(response))
    else:
        info = 'student schedule'
    return str(info)[:4096]
