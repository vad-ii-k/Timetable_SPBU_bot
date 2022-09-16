from dataclasses import dataclass


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
