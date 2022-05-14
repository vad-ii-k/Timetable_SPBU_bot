import random
from datetime import date
from typing import Dict, List, Tuple

import aiohttp
from aiohttp_socks import ProxyConnector

from tgbot.config import PROXY_LOGIN, PROXY_PASSWORD, PROXY_IPS
from utils.db_api.db_timetable import add_timetable_to_db
from utils.timetable.helpers import calculator_of_week_days


async def request(url: str) -> Dict:
    ip = PROXY_IPS[random.randint(0, len(PROXY_IPS) - 1)]
    connector = ProxyConnector.from_url(f'HTTP://{PROXY_LOGIN}:{PROXY_PASSWORD}@{ip}')
    async with aiohttp.ClientSession(connector=connector) as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                return await resp.json()
            return {}

TT_API_URL = "https://timetable.spbu.ru/api/v1"


async def teacher_search(last_name: str) -> List[Dict[str, str]]:
    url = TT_API_URL + f"/educators/search/{last_name}"
    response = await request(url)

    teachers = []
    if response.get("Educators") is not None:
        for teacher in response["Educators"]:
            teachers.append({"Id": teacher["Id"], "FullName": teacher["FullName"]})
    return teachers


async def get_study_divisions() -> List[Dict[str, str]]:
    url = TT_API_URL + "/study/divisions"
    response = await request(url)

    study_divisions = []
    for division in response:
        study_divisions.append({"Alias": division["Alias"], "Name": division["Name"]})
    return study_divisions


async def get_study_levels(alias: str) -> Tuple[List[Dict[str, str]], Dict]:
    url = TT_API_URL + f"/study/divisions/{alias}/programs/levels"
    response = await request(url)

    study_levels = []
    for serial, level in enumerate(response):
        study_levels.append({"StudyLevelName": level["StudyLevelName"], "Serial": serial})
    return study_levels, response


async def get_groups(program_id: str) -> List[Dict[str, str]]:
    url = TT_API_URL + f"/progams/{program_id}/groups"
    response = await request(url)

    groups = []
    for group in response["Groups"]:
        groups.append({"StudentGroupId": group["StudentGroupId"], "StudentGroupName": group["StudentGroupName"]})
    return groups


async def fill_timetable_from_tt(tt_id: int, user_type: str) -> None:
    """ We get the schedule for the rest of the current half-year """
    monday = (await calculator_of_week_days(week_counter=-1))[0]
    url = TT_API_URL + ("/groups" if user_type == 'student' else "/educators") + f"/{tt_id}/events/{monday}/"
    url += f"{monday.year}-08-01" if monday < date(monday.year, 8, 1) else f"{monday.year + 1}-02-01"
    response = await request(url)

    if user_type == 'student':
        if len(response["Days"]) > 0:
            for day in response["Days"]:
                await add_timetable_to_db(day["DayStudyEvents"], tt_id, user_type)
    else:
        if len(response["EducatorEventsDays"]) > 0:
            for day in response["EducatorEventsDays"]:
                await add_timetable_to_db(day["DayStudyEvents"], tt_id, user_type, response["EducatorLongDisplayText"])
