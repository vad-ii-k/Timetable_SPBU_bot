from datetime import date
from typing import Final

from tgbot.data_classes import (
    StudyDivision,
    EducatorSearchInfo,
    StudyLevel,
    AdmissionYear,
    ProgramCombination,
    GroupSearchInfo,
)
from tgbot.misc.states import UserType
from tgbot.services.timetable_api.api_request import request
from tgbot.services.timetable_api.helpers import _get_monday_and_sunday_dates

TT_API_URL: Final[str] = "https://timetable.spbu.ru/api/v1"


async def get_study_divisions() -> list[StudyDivision]:
    url = f"{TT_API_URL}/study/divisions"
    response = await request(url, 60 * 60 * 24 * 10)

    study_divisions: list[StudyDivision] = []
    for division in response:
        study_divisions.append(StudyDivision(alias=division["Alias"], name=division["Name"]))
    return study_divisions


async def educator_search(last_name: str) -> list[EducatorSearchInfo]:
    url = f"{TT_API_URL}/educators/search/{last_name}"
    response = await request(url, 60 * 60 * 24 * 3)

    educators: list[EducatorSearchInfo] = []
    if "Educators" in response:
        for educator in response["Educators"]:
            educators.append(EducatorSearchInfo(tt_id=educator["Id"], full_name=educator["FullName"]))
    return educators


async def get_study_levels(alias: str) -> list[StudyLevel]:
    url = f"{TT_API_URL}/study/divisions/{alias}/programs/levels"
    response = await request(url, 60 * 60 * 24 * 10)

    study_levels: list[StudyLevel] = []
    for level in response:
        response_program_combinations = level["StudyProgramCombinations"]
        program_combinations: list[ProgramCombination] = []
        for program in response_program_combinations:
            admission_years: list[AdmissionYear] = []
            response_admission_years = program["AdmissionYears"]
            for year in response_admission_years:
                admission_years.append(AdmissionYear(year=year["YearName"], study_program_id=year["StudyProgramId"]))
            program_combinations.append(ProgramCombination(name=program["Name"], admission_years=admission_years))
        study_level = StudyLevel(name=level["StudyLevelName"], program_combinations=program_combinations)
        study_levels.append(study_level)
    return study_levels


async def get_groups(program_id: str) -> list[GroupSearchInfo]:
    url = f"{TT_API_URL}/progams/{program_id}/groups"  # Typo in api
    response = await request(url, 60 * 60 * 24 * 10)

    groups: list[GroupSearchInfo] = []
    for group in response["Groups"]:
        groups.append(GroupSearchInfo(tt_id=group["StudentGroupId"], name=group["StudentGroupName"]))
    return groups


async def get_schedule_from_tt(tt_id: int, user_type: UserType) -> dict:
    """We get the schedule for the rest of the current half-year"""
    monday, _ = await _get_monday_and_sunday_dates(week_counter=-1)
    url = f"{TT_API_URL}{'/groups' if user_type.STUDENT else '/educators'}/{tt_id}/events/{monday}/" + \
          f"{monday.year}-08-01" if monday < date(monday.year, 8, 1) else f"{monday.year + 1}-02-01"
    response = await request(url)

    info_about_events_for_semester = response["Days"] if user_type.STUDENT else response["EducatorEventsDays"]
    return info_about_events_for_semester
