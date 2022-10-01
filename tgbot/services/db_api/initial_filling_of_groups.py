import asyncio
import logging
from itertools import cycle
from typing import Iterable, Callable, Coroutine

import aiohttp
from aiohttp_socks import ProxyConnector

from tgbot.config import app_config
from tgbot.data_classes import GroupSearchInfo, StudyLevel
from tgbot.services.timetable_api.timetable_api import TT_API_URL, get_study_divisions

program_ids: list[str] = []
groups: list[GroupSearchInfo] = []
remaining_program_ids: list[str] = []


async def request(session: aiohttp.ClientSession, url: str) -> dict:
    async with session.get(url) as response:
        if response.status == 200:
            return await response.json()
    return {}


def chunks_generator(lst: list[str], chuck_size: int) -> Iterable[list[str]]:
    for i in range(0, len(lst), chuck_size):
        yield lst[i: i + chuck_size]


async def create_and_run_tasks(chunks: list[list[str]], function: Callable[[aiohttp.ClientSession, str], Coroutine]):
    proxies_pool = cycle(app_config.proxy.ips)
    for chunk in chunks:
        connector = ProxyConnector.from_url(
            f"HTTP://{app_config.proxy.login}:{app_config.proxy.password}@{next(proxies_pool)}"
        )
        async with aiohttp.ClientSession(connector=connector) as session:
            tasks = []
            for item in chunk:
                task = asyncio.create_task(function(session, item))
                tasks.append(task)
                await asyncio.sleep(0.05)
            await asyncio.gather(*tasks)


async def get_study_levels(session: aiohttp.ClientSession, alias: str) -> None:
    url = f"{TT_API_URL}/study/divisions/{alias}/programs/levels"
    response = await request(session, url)
    for level in response:
        parsed_level = StudyLevel(**level)
        for program_combination in parsed_level.program_combinations:
            for admission_year in program_combination.admission_years:
                program_ids.append(admission_year.study_program_id)


async def collecting_program_ids() -> None:
    study_divisions = await get_study_divisions()
    # aliases = [division.alias for division in study_divisions]
    aliases = [study_divisions[0].alias]
    aliases_by_parts = list(chunks_generator(aliases, 4))
    await create_and_run_tasks(aliases_by_parts, get_study_levels)


async def get_groups(session: aiohttp.ClientSession, program_id: str) -> None:
    url = f"{TT_API_URL}/progams/{program_id}/groups"
    response = await request(session, url)
    if "Groups" in response:
        for group in response["Groups"]:
            if len(group) != 0:
                groups.append(GroupSearchInfo(tt_id=group["StudentGroupId"], name=group["StudentGroupName"]))
    else:
        remaining_program_ids.append(program_id)


async def adding_groups_to_db() -> None:
    logging.info("Collecting programs...")
    await collecting_program_ids()
    number_of_gathered_programs = 0
    while True:
        global program_ids
        program_ids_by_parts = list(chunks_generator(program_ids, 50))
        await create_and_run_tasks(program_ids_by_parts, get_groups)
        number_of_gathered_programs += len(program_ids)
        logging.info(
            "Groups of %s programs are collected... %s left.", number_of_gathered_programs, len(remaining_program_ids)
        )
        #for group in groups:
        #    await database.add_new_group(tt_id=group.tt_id, group_name=group.name)
        if len(remaining_program_ids) == 0:
            break
        program_ids = remaining_program_ids.copy()
        remaining_program_ids.clear()
