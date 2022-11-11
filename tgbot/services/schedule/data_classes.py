""" Dataclasses for working with a schedule """
from dataclasses import dataclass
from enum import Enum

from pydantic import BaseModel, Field


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


class UserType(str, Enum):
    STUDENT = "student"
    EDUCATOR = "educator"
