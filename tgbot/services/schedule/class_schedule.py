from abc import ABC, abstractmethod
from datetime import time, date
from itertools import groupby
from typing import TypeVar, Generic

from aiogram.utils.i18n import gettext as _
from pydantic import BaseModel, Field, validator, root_validator
from pydantic.generics import GenericModel

from tgbot.services.schedule.helpers import get_schedule_weekday_header, get_time_sticker, get_subject_format_sticker


class StudyEvent(BaseModel, ABC):
    start_time: time = Field(alias="Start")
    end_time: time = Field(alias="End")
    name: str = Field(alias="Subject")
    event_format: str | None
    location: str = Field(alias="LocationsDisplayText")
    is_canceled: bool = Field(alias="IsCancelled")

    @property
    @abstractmethod
    def contingent(self) -> str:
        pass

    @property
    @abstractmethod
    def contingent_sticker(self) -> str:
        pass

    @validator('start_time', 'end_time', pre=True)
    def from_datetime_to_time(cls, value):
        return value.split('T')[1]

    @root_validator
    def separation_of_subject(cls, values):
        values['name'], values['event_format'] = values['name'].rsplit(sep=", ", maxsplit=1) \
            if values['name'].rfind(", ") != -1 else (values['name'], "—")
        return values

    @classmethod
    def __verify_data(cls, other):
        if not isinstance(other, StudyEvent):
            raise TypeError
        return other

    def __ne__(self, other) -> bool:
        event = self.__verify_data(other)
        return (
                self.name != event.name
                or self.event_format != event.event_format
                or self.start_time != event.start_time
                or self.end_time != event.end_time
                or self.is_canceled != event.is_canceled
        )


TSE = TypeVar('TSE')


class EventsDay(GenericModel, Generic[TSE]):
    day: date = Field(alias="Day")
    events: list[TSE] = Field(alias="DayStudyEvents")

    general_location: str | None = None

    @validator('day', pre=True)
    def from_datetime_to_date(cls, value):
        return value.split('T')[0]

    @root_validator
    def combining_locations_of_events(cls, values):
        events: list[TSE] = values['events']
        locations_without_office = list(map(lambda e: e.location.rsplit(",", maxsplit=1)[0], events))
        if locations_without_office.count(locations_without_office[0]) == len(locations_without_office):
            values['general_location'] = locations_without_office[0]
            for value in events:
                if value.location.rfind(",") != -1:
                    value.location = value.location.rsplit(",", maxsplit=1)[1].strip(' ')
                else:
                    value.location = '—'
            values['events'] = events
        return values

    async def events_day_converter_to_msg(self) -> str:
        day_timetable = "\n\n" + await get_schedule_weekday_header(self.day, self.general_location)

        def key_func(event: StudyEvent):
            return event.name, event.event_format, event.start_time, event.end_time, event.is_canceled

        for (name, event_format, start_time, end_time, is_canceled), subjects in groupby(self.events, key=key_func):
            day_timetable += (
                f'     ┈┈┈┈┈┈┈┈┈┈┈┈\n'
                f'    {"<s>" * is_canceled}<b>{name}</b>{"</s>" * is_canceled}\n'
                f'    {get_time_sticker(start_time.hour)} {start_time:%H:%M}-{end_time:%H:%M}\n'
                f'    <i>{get_subject_format_sticker(event_format)} {event_format}</i>\n'
            )
            for subject in subjects:
                day_timetable += (
                    f"    <i>{subject.contingent_sticker}{subject.contingent}\n"
                    f"    {'🚪 каб.' if self.general_location else '📍'} {subject.location}</i>\n"
                )
        return day_timetable


class Schedule(BaseModel, ABC):
    tt_url: str
    from_date: date
    to_date: date
    day: date = None

    @property
    def header_week(self):
        try:
            week = _("📆 Неделя: ") + f'<a href="{self.tt_url}">{self.from_date:%d.%m} — {self.to_date:%d.%m}</a>\n'
        except LookupError:
            week = f'📆 Неделя: <a href="{self.tt_url}">{self.from_date:%d.%m} — {self.to_date:%d.%m}</a>\n'
        return week

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def header_name(self) -> str:
        pass

    async def get_schedule_week_header(self) -> str:
        return self.header_name + self.header_week


class EducatorStudyEvent(StudyEvent):
    groups: str = Field(alias="ContingentUnitName")

    @property
    def contingent(self) -> str:
        return self.groups

    @property
    def contingent_sticker(self) -> str:
        return '🎓 '


class EducatorSchedule(Schedule):
    educator_tt_id: int = Field(alias="EducatorMasterId")
    full_name: str = Field(alias="EducatorLongDisplayText")
    events_days: list[EventsDay[EducatorStudyEvent]] = Field(alias="EducatorEventsDays")

    @property
    def name(self):
        return self.full_name

    @property
    def header_name(self) -> str:
        try:
            header_name = _("🧑‍🏫 Преподаватель: ") + f"<b>{self.name}</b>\n"
        except LookupError:
            header_name = f'🧑‍🏫 Преподаватель: <b>{self.name}</b>\n'
        return header_name


class GroupStudyEvent(StudyEvent):
    educators: str = Field(alias="EducatorsDisplayText")

    @property
    def contingent(self) -> str:
        return self.educators

    @property
    def contingent_sticker(self) -> str:
        return '👨🏻‍🏫 '

    @validator('educators', pre=True)
    def removing_academic_degrees(cls, educators):
        if educators == '':
            return '—'
        return "".join(_educator.rsplit(", ", maxsplit=1)[0] + "; " for _educator in educators.split(sep=";"))[:-2]


class GroupSchedule(Schedule):
    group_tt_id: int = Field(alias="StudentGroupId")
    group_name: str = Field(alias="StudentGroupDisplayName")
    events_days: list[EventsDay[GroupStudyEvent]] = Field(alias="Days")

    @property
    def name(self):
        return self.group_name

    @property
    def header_name(self) -> str:
        try:
            header_name = _("👨‍👩‍👧‍👦 Группа: ") + f"<b>{self.name}</b>\n"
        except LookupError:
            header_name = f'👨‍👩‍👧‍👦 Группа: <b>{self.name}</b>\n'
        return header_name
