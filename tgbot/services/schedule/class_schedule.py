""" Classes for working with a schedule """

from abc import ABC, abstractmethod
from datetime import date, time
from itertools import groupby
from typing import Generic, Self, TypeVar

from aiogram.utils.i18n import gettext as _
from pydantic import BaseModel, Field, field_validator, model_validator

from tgbot.services.schedule.helpers import get_schedule_weekday_header, get_subject_format_sticker, get_time_sticker


class StudyEvent(BaseModel, ABC):
    """Timetable study event"""

    start_time: time = Field(alias="Start")
    end_time: time = Field(alias="End")
    name: str = Field(alias="Subject")
    event_format: str | None = None
    location: str = Field(alias="LocationsDisplayText")
    is_canceled: bool = Field(alias="IsCancelled")

    @property
    @abstractmethod
    def contingent(self) -> str:
        """Property for getting an educator or group related to an event"""

    @property
    @abstractmethod
    def contingent_sticker(self) -> str:
        """Property for getting an educator or group sticker"""

    @field_validator("start_time", "end_time", mode="before")
    def from_datetime_to_time(cls, value: str):
        """
        Separating time from datetime
        :param value: example *2022-11-14T11:05:00*
        :return: example *11:05:00*
        """
        return value.split("T")[1]

    @field_validator("location", mode="before")
    def clearing_location(cls, value: str):
        """
        Validator for cleaning location so that bot can parse html-tags
        :param value: example *Университетский проспект, д. 28, лит. А,1*,\n
            example to be cleaned *<по месту проведения>, <по месту проведения>*
        :return: example *Университетский проспект, д. 28, лит. А,1*,\n
            example to be cleaned *по месту проведения, по месту проведения*
        """
        return value.replace("<", "").replace(">", "")

    @model_validator(mode="after")
    def separation_of_subject(cls, values: Self):
        """
        Separation of subject into name and type of event
        :param values: example *Методы вычислений и вычислительный практикум, лекция*
        :return:
        """
        values.name, values.event_format = (
            values.name.rsplit(sep=", ", maxsplit=1) if values.name.rfind(", ") != -1 else (values.name, "—")
        )
        return values


TypeOfStudyEvents = TypeVar("TypeOfStudyEvents")


class EventsDay(BaseModel, Generic[TypeOfStudyEvents]):
    """Timetable day of events"""

    day: date = Field(alias="Day")
    events: list[TypeOfStudyEvents] = Field(alias="DayStudyEvents")

    general_location: str | None = None

    @field_validator("day", mode="before")
    def from_datetime_to_date(cls, value: str):
        """
        Separating date from datetime
        :param value: example *2022-11-14T11:05:00*
        :return: example *2022-11-14*
        """
        return value.split("T")[0]

    @model_validator(mode="after")
    def combining_locations_of_events(cls, values: Self):
        """
        Validator separates addresses of all events of the day from cabinet and,
        if addresses match, records address in general_location, and replaces locations with cabinet number
        :param values:
        :return:
        """
        locations_without_office = list(map(lambda e: e.location.rsplit(",", maxsplit=1)[0], values.events))
        if locations_without_office.count(locations_without_office[0]) == len(locations_without_office):
            values.general_location = locations_without_office[0]
            for value in values.events:
                if value.location.rfind(",") != -1:
                    value.location = value.location.rsplit(",", maxsplit=1)[1].strip(" ")
                else:
                    value.location = "—"
        return values

    async def events_day_converter_to_msg(self) -> str:
        """
        Converting a class schedule into a text message
        :return:
        """
        day_timetable = "\n\n" + await get_schedule_weekday_header(self.day, self.general_location)

        def key_func(event: StudyEvent):
            return (
                event.name,
                event.event_format,
                event.start_time,
                event.end_time,
                event.is_canceled,
            )

        for (name, event_format, start_time, end_time, is_canceled), subjects in groupby(self.events, key=key_func):
            day_timetable += (
                f"     ┈┈┈┈┈┈┈┈┈┈┈┈\n"
                f'    {"<s>" * is_canceled}<b>{name}</b>{"</s>" * is_canceled}\n'
                f"    {get_time_sticker(start_time.hour)} {start_time:%H:%M}-{end_time:%H:%M}\n"
            )
            if event_format:
                day_timetable += f"    <i>{get_subject_format_sticker(event_format)} {event_format}</i>\n"
            for subject in subjects:
                day_timetable += (
                    f"    <i>{subject.contingent_sticker}{subject.contingent}\n"
                    f"    {'🚪 каб.' if self.general_location else '📍'} {subject.location}</i>\n"
                )
        return day_timetable


class Schedule(BaseModel, ABC):
    """Abstract class for schedule"""

    tt_url: str
    from_date: date
    to_date: date
    day: date = None

    @property
    def header_week(self) -> str:
        """
        Property for getting a headline with information about week for a text schedule
        :return:
        """
        try:
            week = _("📆 Неделя: ") + f'<a href="{self.tt_url}">{self.from_date:%d.%m} — {self.to_date:%d.%m}</a>\n'
        except LookupError:
            week = f'📆 Неделя: <a href="{self.tt_url}">{self.from_date:%d.%m} — {self.to_date:%d.%m}</a>\n'
        return week

    @property
    @abstractmethod
    def name(self) -> str:
        """Property for getting full name of educator or name of group"""

    @property
    @abstractmethod
    def header_name(self) -> str:
        """Property for getting a headline with information about educator or group"""

    async def get_schedule_week_header(self) -> str:
        """
        Combining two parts of header
        :return:
        """
        return self.header_name + self.header_week


class EducatorStudyEvent(StudyEvent):
    """Class for educator's study event"""

    groups: str = Field(alias="ContingentUnitName")

    @property
    def contingent(self) -> str:
        return self.groups

    @property
    def contingent_sticker(self) -> str:
        return "🎓 "


class EducatorSchedule(Schedule):
    """Class for educator's schedule"""

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
            header_name = f"🧑‍🏫 Преподаватель: <b>{self.name}</b>\n"
        return header_name


class GroupStudyEvent(StudyEvent):
    """Class for group's study event"""

    educators: str = Field(alias="EducatorsDisplayText")

    @property
    def contingent(self) -> str:
        return self.educators

    @property
    def contingent_sticker(self) -> str:
        return "👨🏻‍🏫 "

    @field_validator("educators", mode="before")
    def removing_academic_degrees(cls, educators: str):
        """
        Removing a teacher's academic degree
        :param educators: example *Лебедева А. В., доцент*
        :return: example *Лебедева А. В.*
        """
        if educators == "":
            return "—"
        return "".join(_educator.rsplit(", ", maxsplit=1)[0] + "; " for _educator in educators.split(sep=";"))[:-2]


class GroupSchedule(Schedule):
    """Class for group's schedule"""

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
            header_name = f"👨‍👩‍👧‍👦 Группа: <b>{self.name}</b>\n"
        return header_name
