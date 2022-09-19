from typing import Final

from tgbot.data_classes import (
    StudyDivision,
    EducatorSearchInfo,
    StudyLevel,
    AdmissionYear,
    ProgramCombination,
    GroupSearchInfo,
)
from tgbot.services.timetable_api.api_request import request

TT_API_URL: Final[str] = "https://timetable.spbu.ru/api/v1"


async def get_study_divisions() -> list[StudyDivision]:
    url = f"{TT_API_URL}/study/divisions"
    response = await request(url)

    study_divisions: list[StudyDivision] = []
    for division in response:
        study_divisions.append(StudyDivision(alias=division["Alias"], name=division["Name"]))
    return study_divisions


async def educator_search(last_name: str) -> list[EducatorSearchInfo]:
    url = f"{TT_API_URL}/educators/search/{last_name}"
    response = await request(url)

    educators: list[EducatorSearchInfo] = []
    if "Educators" in response:
        for educator in response["Educators"]:
            educators.append(EducatorSearchInfo(tt_id=educator["Id"], full_name=educator["FullName"]))
    return educators


async def get_study_levels(alias: str) -> list[StudyLevel]:
    url = f"{TT_API_URL}/study/divisions/{alias}/programs/levels"
    response = await request(url)

    study_levels: list[StudyLevel] = []
    for serial_1, level in enumerate(response):
        response_program_combinations = response[serial_1]["StudyProgramCombinations"]
        program_combinations: list[ProgramCombination] = []
        for serial_2, program in enumerate(response_program_combinations):
            admission_years: list[AdmissionYear] = []
            response_admission_years = response_program_combinations[serial_2]["AdmissionYears"]
            for year in response_admission_years:
                admission_years.append(AdmissionYear(year=year["YearName"], study_program_id=year["StudyProgramId"]))
            program_combinations.append(ProgramCombination(name=program["Name"], admission_years=admission_years))
        study_level = StudyLevel(name=level["StudyLevelName"], program_combinations=program_combinations)
        study_levels.append(study_level)
    return study_levels


async def get_groups(program_id: str) -> list[GroupSearchInfo]:
    url = f"{TT_API_URL}/progams/{program_id}/groups"
    response = await request(url)

    groups: list[GroupSearchInfo] = []
    for group in response["Groups"]:
        groups.append(GroupSearchInfo(tt_id=group["StudentGroupId"], name=group["StudentGroupName"]))
    return groups
