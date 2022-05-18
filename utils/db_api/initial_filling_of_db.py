import asyncio
import os
from itertools import cycle
from typing import Dict, List, Iterable

import aiohttp
from aiohttp_socks import ProxyConnector

from tgbot.config import PROXY_IPS, PROXY_LOGIN, PROXY_PASSWORD
from tgbot.loader import db
from utils.timetable.api import TT_API_URL

program_ids: List[str] = []
groups: List[Dict[str, str]] = []
remaining_program_ids: List[str] = []


async def request(session: aiohttp.ClientSession, url: str) -> Dict:
    try:
        async with session.get(url) as response:
            print(url)
            if response.status == 200:
                return await response.json()
            print(f"Error code: {response.status}")
            return {}
    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")
        return {}


async def get_study_divisions() -> List[Dict[str, str]]:
    url = f"{TT_API_URL}/study/divisions"
    async with aiohttp.ClientSession() as session:
        response = await request(session, url)

    study_divisions = []
    for division in response:
        study_divisions.append({"Alias": division["Alias"], "Name": division["Name"]})
    return study_divisions


async def collecting_program_ids() -> None:
    aliases = [item["Alias"] for item in (await get_study_divisions())]
    aliases_by_parts = list(chunks_generator(aliases, 4))
    proxies_pool = cycle(PROXY_IPS)
    for chunk in aliases_by_parts:
        connector = ProxyConnector.from_url(
            f"HTTP://{PROXY_LOGIN}:{PROXY_PASSWORD}@{next(proxies_pool)}"
        )
        async with aiohttp.ClientSession(connector=connector) as session:
            tasks = []
            for alias in chunk:
                task = asyncio.create_task(get_study_levels(session, alias))
                tasks.append(task)
            await asyncio.gather(*tasks)


async def get_study_levels(session: aiohttp.ClientSession, alias: str) -> None:
    url = f"{TT_API_URL}/study/divisions/{alias}/programs/levels"
    response = await request(session, url)
    for level in response:
        program_combinations = level["StudyProgramCombinations"]
        for program_combination in program_combinations:
            for year in program_combination["AdmissionYears"]:
                program_ids.append(str(year["StudyProgramId"]))


async def get_groups(session: aiohttp.ClientSession, program_id: str) -> None:
    url = f"{TT_API_URL}/progams/{program_id}/groups"
    response = await request(session, url)
    if "Groups" in response:
        for group in response["Groups"]:
            if len(group) != 0:
                groups.append(
                    {
                        "GroupId": group["StudentGroupId"],
                        "GroupName": group["StudentGroupName"],
                    }
                )
    else:
        remaining_program_ids.append(program_id)


def chunks_generator(lst: List[str], chuck_size: int) -> Iterable[List[str]]:
    for i in range(0, len(lst), chuck_size):
        yield lst[i: i + chuck_size]


async def collecting_groups_info(_program_ids: List[str]) -> None:
    program_ids_by_parts = list(chunks_generator(_program_ids, 100))
    proxies_pool = cycle(PROXY_IPS)
    for chunk in program_ids_by_parts:
        connector = ProxyConnector.from_url(
            f"HTTP://{PROXY_LOGIN}:{PROXY_PASSWORD}@{next(proxies_pool)}"
        )
        async with aiohttp.ClientSession(connector=connector) as session:
            tasks = []
            for program_id in chunk:
                task = asyncio.create_task(get_groups(session, program_id))
                tasks.append(task)
                await asyncio.sleep(0.06)
            await asyncio.gather(*tasks)


async def adding_groups_to_db() -> None:
    with open("data/program_ids.txt", "r+", encoding='UTF-8') as file:
        file_size = os.stat(file.name).st_size
        if file_size == 0:
            await collecting_program_ids()
        elif file_size != 1:
            for program_id in file.readline().split(" "):
                program_ids.append(program_id)
    if file_size != 1:
        await collecting_groups_info(program_ids)
        for group in groups:
            await db.add_new_group(tt_id=group["GroupId"], group_name=group["GroupName"])

        with open("data/program_ids.txt", "w", encoding='UTF-8') as file:
            str_to_write = "".join([program_id + " " for program_id in remaining_program_ids])
            file.write(str_to_write[:-1])
            if len(remaining_program_ids) == 0:
                file.write(" ")
