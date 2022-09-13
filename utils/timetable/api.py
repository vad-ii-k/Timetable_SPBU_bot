from datetime import date
from random import shuffle
from typing import Dict, List, Tuple

import aiohttp
from aiohttp_client_cache import CachedSession, RedisBackend
from aiohttp_socks import ProxyConnector, ProxyError

from tgbot.config import PROXY_IPS, PROXY_LOGIN, PROXY_PASSWORD, REDIS_HOST, REDIS_PORT, REDIS_PASSWORD
from utils.db_api.db_timetable import add_timetable_to_db
from utils.timetable.helpers import calculator_of_week_days


def get_cache(expire_after: int):
    redis_cache = RedisBackend(
        cache_name='aiohttp-cache',
        address=f'redis://{REDIS_HOST}',
        port=REDIS_PORT,
        password=REDIS_PASSWORD,
        db=2,
        expire_after=expire_after,
    )
    return redis_cache


async def request(url: str, expire_after: int) -> Dict:
    shuffle(PROXY_IPS)
    # Iterating through the proxy until we get the OK status
    for proxy_ip in PROXY_IPS:
        connector = ProxyConnector.from_url(f'HTTP://{PROXY_LOGIN}:{PROXY_PASSWORD}@{proxy_ip}')
        async with CachedSession(cache=get_cache(expire_after=expire_after), connector=connector) as session:
            try:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        return await resp.json()
            except ProxyError:
                break
    # Trying to get a response without a proxy
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                return await resp.json()
    return {}


TT_API_URL = "https://timetable.spbu.ru/api/v1"


async def teacher_search(last_name: str) -> List[Dict[str, str]]:
    url = f"{TT_API_URL}/educators/search/{last_name}"
    response = await request(url, 60 * 60 * 24 * 3)

    teachers = []
    if "Educators" in response:
        for teacher in response["Educators"]:
            teachers.append({"Id": teacher["Id"], "FullName": teacher["FullName"]})
    return teachers


async def get_study_divisions() -> List[Dict[str, str]]:
    url = f"{TT_API_URL}/study/divisions"
    response = await request(url, 60 * 60 * 24 * 10)

    study_divisions = []
    for division in response:
        study_divisions.append({"Alias": division["Alias"], "Name": division["Name"]})
    return study_divisions


async def get_study_levels(alias: str) -> Tuple[List[Dict[str, str]], Dict]:
    url = f"{TT_API_URL}/study/divisions/{alias}/programs/levels"
    response = await request(url, 60 * 60 * 24 * 10)

    study_levels = []
    for serial, level in enumerate(response):
        study_levels.append({"StudyLevelName": level["StudyLevelName"], "Serial": serial})
    return study_levels, response


async def get_groups(program_id: str) -> List[Dict[str, str]]:
    url = f"{TT_API_URL}/progams/{program_id}/groups"
    response = await request(url, 60 * 60 * 24 * 10)

    groups = []
    for group in response["Groups"]:
        groups.append(
            {
                "StudentGroupId": group["StudentGroupId"],
                "StudentGroupName": group["StudentGroupName"],
            }
        )
    return groups


async def fill_timetable_from_tt(tt_id: int, user_type: str) -> None:
    """We get the schedule for the rest of the current half-year"""
    monday = (await calculator_of_week_days(week_counter=-1))[0]
    url = f"{TT_API_URL}{'/groups' if user_type == 'student' else '/educators'}/" \
          f"{tt_id}/events/{monday}/" + \
          (f"{monday.year}-08-01" if monday < date(monday.year, 8, 1) else f"{monday.year + 1}-02-01")
    response = await request(url, 60 * 60 * 10)

    days_info = response["Days"] if user_type == "student" else response["EducatorEventsDays"]
    if len(days_info) > 0:
        for day in days_info:
            await add_timetable_to_db(
                events=day["DayStudyEvents"],
                tt_id=tt_id,
                user_type=user_type,
                full_name=response["EducatorLongDisplayText"] if user_type == 'teacher' else None
            )
