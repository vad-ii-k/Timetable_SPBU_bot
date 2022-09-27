from dataclasses import dataclass
from datetime import time, date

from pydantic import BaseModel, Field, validator


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


class StudyEvent(BaseModel):
    start_time: time = Field(alias="Start")
    end_time: time = Field(alias="End")
    subject: str = Field(alias="Subject")
    location: str = Field(alias="LocationsDisplayText")
    is_canceled: bool = Field(alias="IsCancelled")
    groups: str = Field(alias="ContingentUnitName")

    @validator('start_time', 'end_time', pre=True)
    def from_datetime_to_time(cls, value):
        return value.split('T')[1]


class EducatorEventsDay(BaseModel):
    day: date = Field(alias="Day")
    study_events: list[StudyEvent] = Field(alias="DayStudyEvents")

    @validator('day', pre=True)
    def from_datetime_to_date(cls, value):
        return value.split('T')[0]


class EducatorSchedule(BaseModel):
    educator_tt_id: int = Field(alias="EducatorMasterId")
    full_name: str = Field(alias="EducatorLongDisplayText")
    events_days: list[EducatorEventsDay] = Field(alias="EducatorEventsDays")