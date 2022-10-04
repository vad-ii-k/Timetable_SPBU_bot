from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import time, date
from typing import TypeVar

from aiogram.utils.i18n import gettext as _, get_i18n
from babel.dates import format_date
from pydantic import BaseModel, Field, validator, root_validator

from tgbot.services.schedule.helpers import _get_schedule_weekday_header, _get_time_sticker, _get_subject_format_sticker


@dataclass(slots=True, frozen=True)
class StudyDivision:
    alias: str
    name: str


@dataclass(slots=True, frozen=True)
class EducatorSearchInfo:
    tt_id: int
    full_name: str


class AdmissionYear(BaseModel):
    year: str = Field(alias="YearName")
    study_program_id: str = Field(alias="StudyProgramId")


class ProgramCombination(BaseModel):
    name: str = Field(alias="Name")
    admission_years: list[AdmissionYear] = Field(alias="AdmissionYears")


class StudyLevel(BaseModel):
    name: str = Field(alias="StudyLevelName")
    program_combinations: list[ProgramCombination] = Field(alias="StudyProgramCombinations")


@dataclass(slots=True, frozen=True)
class GroupSearchInfo:
    tt_id: int
    name: str


SE = TypeVar('SE', bound='StudyEvent')


class StudyEvent(BaseModel, ABC):
    start_time: time = Field(alias="Start")
    end_time: time = Field(alias="End")
    subject_name: str = Field(alias="Subject")
    subject_format: str | None
    location: str = Field(alias="LocationsDisplayText")
    is_canceled: bool = Field(alias="IsCancelled")

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
    def __verify_data(cls, other) -> SE:
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


class EventsDay(BaseModel):
    day: date = Field(alias="Day")

    @validator('day', pre=True)
    def from_datetime_to_date(cls, value):
        return value.split('T')[0]

    @property
    @abstractmethod
    def events(self):
        pass

    async def events_day_converter_to_msg(self, day: date) -> str:
        day_timetable = _get_schedule_weekday_header(format_date(day, "EEEE, d MMMM", locale=get_i18n().current_locale))
        for i, event in enumerate(self.events):
            if i == 0 or self.events[i - 1] != event:
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


class Schedule(BaseModel, ABC):
    tt_url: str
    from_date: date
    to_date: date

    @abstractmethod
    async def get_schedule_week_header(self) -> str:
        pass

    @property
    @abstractmethod
    def name(self):
        pass


class EducatorStudyEvent(StudyEvent):
    groups: str = Field(alias="ContingentUnitName")

    def get_contingent(self, with_sticker: bool = False) -> str:
        return '🎓 ' * with_sticker + self.groups


class EducatorEventsDay(EventsDay):
    study_events: list[EducatorStudyEvent] = Field(alias="DayStudyEvents")

    @property
    def events(self):
        return self.study_events


class EducatorSchedule(Schedule):
    educator_tt_id: int = Field(alias="EducatorMasterId")
    _full_name: str = Field(alias="EducatorLongDisplayText")
    events_days: list[EducatorEventsDay] = Field(alias="EducatorEventsDays")

    @property
    def name(self):
        return self._full_name

    async def get_schedule_week_header(self) -> str:
        header = _("🧑‍🏫 Преподаватель: ") + f"<b>{self._full_name}</b>\n" \
                 + _("📆 Неделя: ") + f'<a href="{self.tt_url}">{self.from_date:%d.%m} — {self.to_date:%d.%m}</a>\n'
        return header


class GroupStudyEvent(StudyEvent):
    educators: str = Field(alias="EducatorsDisplayText")

    @validator('educators', pre=True)
    def removing_academic_degrees(cls, educators):
        educators = "".join(_educator.rsplit(", ", maxsplit=1)[0] + "; " for _educator in educators.split(sep=";"))[:-2]
        if educators == '':
            educators = '—'
        return educators

    def get_contingent(self, with_sticker: bool = False) -> str:
        return '👨🏻‍🏫 ' * with_sticker + self.educators


class GroupEventsDay(EventsDay):
    study_events: list[GroupStudyEvent] = Field(alias="DayStudyEvents")

    @property
    def events(self):
        return self.study_events


class GroupSchedule(Schedule):
    group_tt_id: int = Field(alias="StudentGroupId")
    _group_name: str = Field(alias="StudentGroupDisplayName")
    events_days: list[GroupEventsDay] = Field(alias="Days")

    @property
    @abstractmethod
    def name(self):
        return self._group_name

    async def get_schedule_week_header(self) -> str:
        header = _("👨‍👩‍👧‍👦 Группа: ") + f"<b>{self._group_name}</b>\n"\
                 + _("📆 Неделя: ") + f'<a href="{self.tt_url}">{self.from_date:%d.%m} — {self.to_date:%d.%m}</a>\n'
        return header
