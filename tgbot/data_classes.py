from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import time, date

from pydantic import BaseModel, Field, validator, root_validator


@dataclass(slots=True, frozen=True)
class StudyDivision:
    alias: str
    name: str


@dataclass(slots=True, frozen=True)
class EducatorSearchInfo:
    tt_id: int
    full_name: str


@dataclass(slots=True, frozen=True)
class AdmissionYear:
    year: str
    study_program_id: str


@dataclass(slots=True, frozen=True)
class ProgramCombination:
    name: str
    admission_years: list[AdmissionYear]


@dataclass(slots=True, frozen=True)
class StudyLevel:
    name: str
    program_combinations: list[ProgramCombination]


@dataclass(slots=True, frozen=True)
class GroupSearchInfo:
    tt_id: int
    name: str


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
        values['subject_name'], values['subject_format'] = values['subject_name'].rsplit(sep=", ", maxsplit=1)
        return values

    @abstractmethod
    def get_contingent(self, with_sticker: bool = False) -> str:
        pass


class EventsDay(BaseModel):
    day: date = Field(alias="Day")

    @validator('day', pre=True)
    def from_datetime_to_date(cls, value):
        return value.split('T')[0]


class EducatorStudyEvent(StudyEvent):
    groups: str = Field(alias="ContingentUnitName")

    def get_contingent(self, with_sticker: bool = False) -> str:
        return '🎓 ' * with_sticker + self.groups


class EducatorEventsDay(EventsDay):
    study_events: list[EducatorStudyEvent] = Field(alias="DayStudyEvents")


class EducatorSchedule(BaseModel):
    educator_tt_id: int = Field(alias="EducatorMasterId")
    full_name: str = Field(alias="EducatorLongDisplayText")
    events_days: list[EducatorEventsDay] = Field(alias="EducatorEventsDays")


class GroupStudyEvent(StudyEvent):
    educators: str = Field(alias="EducatorsDisplayText")

    @validator('educators', pre=True)
    def removing_academic_degrees(cls, educators):
        educators = "".join(_educator.rsplit(", ", maxsplit=1)[0] + "; " for _educator in educators.split(sep=";"))[:-2]
        return educators

    def get_contingent(self, with_sticker: bool = False) -> str:
        return '🧑‍🏫 ' * with_sticker + self.educators


class GroupEventsDay(EventsDay):
    study_events: list[GroupStudyEvent] = Field(alias="DayStudyEvents")


class GroupSchedule(BaseModel):
    student_tt_id: int = Field(alias="StudentGroupId")
    group_name: str = Field(alias="StudentGroupDisplayName")
    events_days: list[GroupEventsDay] = Field(alias="Days")
