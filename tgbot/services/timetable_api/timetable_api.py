""" Wrappers over the timetable API """
from typing import Final

from cashews import cache

from tgbot.config import app_config
from tgbot.services.schedule.class_schedule import EducatorSchedule, GroupSchedule
from tgbot.services.schedule.data_classes import EducatorSearchInfo, GroupSearchInfo, StudyDivision, StudyLevel
from tgbot.services.timetable_api.api_request import request

TT_API_URL: Final[str] = "https://timetable.spbu.ru/api/v1"
TT_URL: Final[str] = "https://timetable.spbu.ru/"

cache.setup(app_config.redis.connection_url, db=2)


@cache(ttl="10d")
async def get_study_divisions() -> list[StudyDivision]:
    """

    :return:
    """
    url = f"{TT_API_URL}/study/divisions"
    response = await request(url)

    study_divisions: list[StudyDivision] = []
    for division in response:
        study_divisions.append(StudyDivision(alias=division["Alias"], name=division["Name"]))
    return study_divisions


@cache(ttl="1d")
async def educator_search(last_name: str) -> list[EducatorSearchInfo]:
    """

    :param last_name:
    :return:
    """
    url = f"{TT_API_URL}/educators/search/{last_name}"
    response = await request(url)

    educators: list[EducatorSearchInfo] = []
    if "Educators" in response:
        for educator in response["Educators"]:
            educators.append(EducatorSearchInfo(tt_id=educator["Id"], full_name=educator["FullName"]))
    return educators


@cache(ttl="1d")
async def get_study_levels(alias: str) -> list[StudyLevel]:
    """

    :param alias:
    :return:
    """
    url = f"{TT_API_URL}/study/divisions/{alias}/programs/levels"
    response = await request(url)

    study_levels: list[StudyLevel] = []
    for level in response:
        study_levels.append(StudyLevel(**level))
    return study_levels


@cache(ttl="1d")
async def get_groups(program_id: int) -> list[GroupSearchInfo]:
    """

    :param program_id:
    :return:
    """
    url = f"{TT_API_URL}/progams/{program_id}/groups"  # Typo in api
    response = await request(url)

    groups: list[GroupSearchInfo] = []
    for group in response["Groups"]:
        groups.append(GroupSearchInfo(tt_id=group["StudentGroupId"], name=group["StudentGroupName"]))
    return groups


@cache(ttl="10h")
async def get_educator_schedule_from_tt(tt_id: int, from_date: str, to_date: str) -> EducatorSchedule:
    """

    :param tt_id:
    :param from_date:
    :param to_date:
    :return:
    """
    url = f"{TT_API_URL}/educators/{tt_id}/events/{from_date}/{to_date}"
    response = await request(url)
    support_info = {
        "tt_url": f"{TT_URL}WeekEducatorEvents/{tt_id}/{from_date}",
        "from_date": from_date,
        "to_date": to_date,
    }
    educator_schedule = EducatorSchedule.model_validate(response | support_info)
    return educator_schedule


@cache(ttl="10h")
async def get_group_schedule_from_tt(tt_id: int, from_date: str, to_date: str) -> GroupSchedule:
    """

    :param tt_id:
    :param from_date:
    :param to_date:
    :return:
    """
    url = f"{TT_API_URL}/groups/{tt_id}/events/{from_date}/{to_date}"
    response = await request(url)
    support_info = {
        "tt_url": f"{TT_URL}MATH/StudentGroupEvents/Primary/{tt_id}/{from_date}",
        "from_date": from_date,
        "to_date": to_date,
    }
    group_schedule = GroupSchedule.model_validate(response | support_info)
    return group_schedule
