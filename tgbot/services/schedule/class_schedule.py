from abc import ABC, abstractmethod
from datetime import time, date
from typing import TypeVar, Generic

from aiogram.utils.i18n import gettext as _
from pydantic import BaseModel, Field, validator, root_validator
from pydantic.generics import GenericModel

from tgbot.services.schedule.helpers import get_schedule_weekday_header, get_time_sticker, get_subject_format_sticker


class StudyEvent(BaseModel, ABC):
    start_time: time = Field(alias="Start")
    end_time: time = Field(alias="End")
    subject_name: str = Field(alias="Subject")
    subject_format: str | None
    location: str = Field(alias="LocationsDisplayText")
    is_canceled: bool = Field(alias="IsCancelled")

    @property
    @abstractmethod
    def contingent(self) -> str:
        pass

    @validator('start_time', 'end_time', pre=True)
    def from_datetime_to_time(cls, value):
        return value.split('T')[1]

    @root_validator
    def separation_of_subject(cls, values):
        values['subject_name'], values['subject_format'] = values['subject_name'].rsplit(sep=", ", maxsplit=1)\
            if values['subject_name'].rfind(", ") != -1 else (values['subject_name'], "—")
        return values

    @abstractmethod
    def get_contingent(self, with_sticker: bool = False) -> str:
        pass

    @classmethod
    def __verify_data(cls, other):
        if not isinstance(other, StudyEvent):
            raise TypeError
        return other

    def __ne__(self, other) -> bool:
        event = self.__verify_data(other)
        return (
                self.subject_name != event.subject_name
                or self.subject_format != event.subject_format
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
        day_timetable = await get_schedule_weekday_header(self.day, self.general_location)
        for i, event in enumerate(self.events):
            if i == 0 or self.events[i - 1] != event:
                day_timetable += (
                    f'     ┈┈┈┈┈┈┈┈┈┈┈┈\n'
                    f'    {"<s>" * event.is_canceled}<b>{event.subject_name}</b>{"</s>" * event.is_canceled}\n'
                    f'    {get_time_sticker(event.start_time.hour)} {event.start_time:%H:%M}-{event.end_time:%H:%M}\n'
                    f'    <i>{get_subject_format_sticker(event.subject_format)} {event.subject_format}</i>\n'
                )
            day_timetable += (
                f"    <i>{event.get_contingent(with_sticker=True)}\n"
                f"    {'🚪 каб.' if self.general_location else '📍'} {event.location}</i>\n"
            )
        return day_timetable


class Schedule(BaseModel, ABC):
    tt_url: str
    from_date: date
    to_date: date
    day: date = None

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    async def get_schedule_week_header(self) -> str:
        pass


class EducatorStudyEvent(StudyEvent):
    groups: str = Field(alias="ContingentUnitName")

    @property
    def contingent(self) -> str:
        return self.groups

    def get_contingent(self, with_sticker: bool = False) -> str:
        return '🎓 ' * with_sticker + self.groups


class EducatorEventsDay(EventsDay[TSE], Generic[TSE]):
    pass


class EducatorSchedule(Schedule):
    educator_tt_id: int = Field(alias="EducatorMasterId")
    full_name: str = Field(alias="EducatorLongDisplayText")
    events_days: list[EducatorEventsDay[EducatorStudyEvent]] = Field(alias="EducatorEventsDays")

    @property
    def name(self):
        return self.full_name

    async def get_schedule_week_header(self) -> str:
        try:
            header = _("🧑‍🏫 Преподаватель: ") + f"<b>{self.name}</b>\n" \
                     + _("📆 Неделя: ") + f'<a href="{self.tt_url}">{self.from_date:%d.%m} — {self.to_date:%d.%m}</a>\n'
        except LookupError:
            header = f'🧑‍🏫 Преподаватель: <b>{self.name}</b>\n' \
                     f'📆 Неделя: <a href="{self.tt_url}">{self.from_date:%d.%m} — {self.to_date:%d.%m}</a>\n'

        return header


class GroupStudyEvent(StudyEvent):
    educators: str = Field(alias="EducatorsDisplayText")

    @property
    def contingent(self) -> str:
        return self.educators

    @validator('educators', pre=True)
    def removing_academic_degrees(cls, educators):
        if educators == '':
            return '—'
        return "".join(_educator.rsplit(", ", maxsplit=1)[0] + "; " for _educator in educators.split(sep=";"))[:-2]

    def get_contingent(self, with_sticker: bool = False) -> str:
        return '👨🏻‍🏫 ' * with_sticker + self.educators


class GroupEventsDay(EventsDay[TSE], Generic[TSE]):
    pass


class GroupSchedule(Schedule):
    group_tt_id: int = Field(alias="StudentGroupId")
    group_name: str = Field(alias="StudentGroupDisplayName")
    events_days: list[GroupEventsDay[GroupStudyEvent]] = Field(alias="Days")

    @property
    def name(self):
        return self.group_name

    async def get_schedule_week_header(self) -> str:
        try:
            header = _("👨‍👩‍👧‍👦 Группа: ") + f"<b>{self.name}</b>\n"\
                     + _("📆 Неделя: ") + f'<a href="{self.tt_url}">{self.from_date:%d.%m} — {self.to_date:%d.%m}</a>\n'
        except LookupError:
            header = f'👨‍👩‍👧‍👦 Группа: <b>{self.name}</b>\n' \
                     f'📆 Неделя: <a href="{self.tt_url}">{self.from_date:%d.%m} — {self.to_date:%d.%m}</a>\n'
        return header
