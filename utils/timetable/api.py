import random
from datetime import date

import aiohttp
from aiohttp_socks import ProxyConnector

from tgbot.config import PROXY_LOGIN, PROXY_PASSWORD, PROXY_IPS
from utils.db_api.db_group_timetable import add_group_timetable_to_db
from utils.db_api.db_teacher_timetable import add_teacher_timetable_to_db
from utils.image_converter.converter import TimetableIMG
from utils.timetable.helpers import calculator_of_days, calculator_of_week_days
from utils.timetable.parsers import teacher_timetable_parser_day, teacher_timetable_week_header, \
    teacher_timetable_day_header


async def request(url: str) -> dict:
    ip = PROXY_IPS[random.randint(0, len(PROXY_IPS) - 1)]
    connector = ProxyConnector.from_url(f'HTTP://{PROXY_LOGIN}:{PROXY_PASSWORD}@{ip}')
    async with aiohttp.ClientSession(connector=connector) as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                return await resp.json()
            else:
                return {}

tt_api_url = "https://timetable.spbu.ru/api/v1"


async def teacher_search(last_name: str) -> list:
    url = tt_api_url + f"/educators/search/{last_name}"
    response = await request(url)

    teachers = []
    for teacher in response["Educators"]:
        teachers.append({"Id": teacher["Id"], "FullName": teacher["FullName"]})
    return teachers


async def fill_teacher_timetable_from_tt(teacher_id: int):
    """ We get the schedule for the rest of the current half-year """
    monday, sunday = await calculator_of_week_days(week_counter=-1)
    url = tt_api_url + f"/educators/{teacher_id}/events/{monday}/"
    august_of_current_year = date(monday.year, 8, 1)
    url += f"{monday.year}-08-01" if monday < august_of_current_year else f"{monday.year+1}-02-01"
    response = await request(url)

    if len(response["EducatorEventsDays"]) > 0:
        for day in response["EducatorEventsDays"]:
            await add_teacher_timetable_to_db(day["DayStudyEvents"], teacher_id, response["EducatorLongDisplayText"])


async def get_study_divisions() -> list:
    url = tt_api_url + "/study/divisions"
    response = await request(url)

    study_divisions = []
    for division in response:
        study_divisions.append({"Alias": division["Alias"], "Name": division["Name"]})
    return study_divisions


async def get_study_levels(alias: str) -> tuple:
    url = tt_api_url + f"/study/divisions/{alias}/programs/levels"
    response = await request(url)

    study_levels = []
    for serial, level in enumerate(response):
        study_levels.append({"StudyLevelName": level["StudyLevelName"], "Serial": serial})
    return study_levels, response


async def get_groups(program_id: str) -> list:
    url = tt_api_url + f"/progams/{program_id}/groups"
    response = await request(url)

    groups = []
    for group in response["Groups"]:
        groups.append({"StudentGroupId": group["StudentGroupId"], "StudentGroupName": group["StudentGroupName"]})
    return groups


async def fill_group_timetable_from_tt(group_id: int):
    """ We get the schedule for the rest of the current half-year """
    monday, sunday = await calculator_of_week_days(week_counter=-1)
    url = tt_api_url + f"/groups/{group_id}/events/{monday}/"
    august_of_current_year = date(monday.year, 8, 1)
    url += f"{monday.year}-08-01" if monday < august_of_current_year else f"{monday.year+1}-02-01"
    response = await request(url)

    if len(response["Days"]) > 0:
        for day in response["Days"]:
            await add_group_timetable_to_db(day["DayStudyEvents"], group_id)
