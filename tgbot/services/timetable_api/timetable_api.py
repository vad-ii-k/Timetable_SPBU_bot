import json
from typing import Final

from tgbot.data_classes import (
    StudyDivision,
    EducatorSearchInfo,
    StudyLevel,
    AdmissionYear,
    ProgramCombination,
    GroupSearchInfo, EducatorSchedule, GroupSchedule,
)
from tgbot.services.timetable_api.api_request import request

TT_API_URL: Final[str] = "https://timetable.spbu.ru/api/v1"
TT_URL: Final[str] = "https://timetable.spbu.ru/"


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


async def get_educator_schedule_from_tt(tt_id: int, from_date: str, to_date: str) -> EducatorSchedule:
    url = f"{TT_API_URL}/educators/{tt_id}/events/{from_date}/{to_date}"
    response = await request(url)
    support_info = {
        "tt_url": f"{TT_URL}WeekEducatorEvents/{tt_id}/{from_date}",
        "from_date": from_date,
        "to_date": to_date
    }
    educator_schedule = EducatorSchedule.parse_raw(json.dumps(response | support_info))
    return educator_schedule


async def get_group_schedule_from_tt(tt_id: int, from_date: str, to_date: str) -> GroupSchedule:
    url = f"{TT_API_URL}/groups/{tt_id}/events/{from_date}/{to_date}"
    response = await request(url)
    support_info = {
        "tt_url": f"{TT_URL}MATH/StudentGroupEvents/Primary/{tt_id}/{from_date}",
        "from_date": from_date,
        "to_date": to_date
    }
    group_schedule = GroupSchedule.parse_raw(json.dumps(response | support_info))
    return group_schedule
