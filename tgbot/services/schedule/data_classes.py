""" Dataclasses for working with a schedule """
from dataclasses import dataclass
from enum import Enum

from pydantic import BaseModel, Field


@dataclass(slots=True, frozen=True)
class StudyDivision:
    """ Dataclass for study division from timetable """
    alias: str
    name: str


@dataclass(slots=True, frozen=True)
class EducatorSearchInfo:
    """ Dataclass for educator's info from timetable """
    tt_id: int
    full_name: str


class AdmissionYear(BaseModel):
    """ Dataclass for admission year from timetable """
    year: str = Field(alias="YearName")
    study_program_id: str = Field(alias="StudyProgramId")


class ProgramCombination(BaseModel):
    """ Dataclass for program combination from timetable """
    name: str = Field(alias="Name")
    admission_years: list[AdmissionYear] = Field(alias="AdmissionYears")


class StudyLevel(BaseModel):
    """ Dataclass for study level from timetable """
    name: str = Field(alias="StudyLevelName")
    program_combinations: list[ProgramCombination] = Field(alias="StudyProgramCombinations")


@dataclass(slots=True, frozen=True)
class GroupSearchInfo:
    """ Dataclass for group's info from timetable """
    tt_id: int
    name: str


class UserType(str, Enum):
    """ User type Enum """
    STUDENT = "student"
    EDUCATOR = "educator"
