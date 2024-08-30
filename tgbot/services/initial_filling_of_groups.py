""" Initial filling of groups for searching by name """

import asyncio
import logging
from itertools import cycle
from typing import Callable, Coroutine, Iterable

from aiohttp import ClientSession
from aiohttp_socks import ProxyConnectionError, ProxyConnector, ProxyError

from tgbot.config import app_config
from tgbot.services.db_api.db_commands import database
from tgbot.services.schedule.data_classes import GroupSearchInfo, StudyLevel
from tgbot.services.timetable_api.timetable_api import TT_API_URL, get_study_divisions

program_ids: list[int] = []
groups: list[GroupSearchInfo] = []
remaining_program_ids: list[str] = []


async def request(session: ClientSession, url: str) -> dict:
    """
    Request to API with [ClientSession](https://docs.aiohttp.org/en/stable/client_reference.html)
    :param session:
    :param url:
    :return:
    """
    try:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.json()
    except ProxyError as err:
        logging.error("Proxy error: %s", err)
    except ProxyConnectionError as err:
        logging.error("Proxy connection error: %s", err)
    return {}


def chunks_generator(arr: list[str], chunk_size: int) -> Iterable[list[str]]:
    """
    Splitting a list into multiple lists
    :param arr:
    :param chunk_size:
    """
    for i in range(0, len(arr), chunk_size):
        yield arr[i : i + chunk_size]


async def create_and_run_tasks(chunks: list[list[str]], function: Callable[[ClientSession, str], Coroutine]):
    """
    Creating and running tasks for asynchronous API requests
    :param chunks:
    :param function:
    """
    proxies_pool = cycle(app_config.proxy.ips)
    for chunk in chunks:
        connector = ProxyConnector.from_url(
            f"HTTP://{app_config.proxy.login}:{app_config.proxy.password}@{next(proxies_pool)}"
        )
        async with ClientSession(connector=connector) as session:
            tasks = []
            for item in chunk:
                task = asyncio.create_task(function(session, item))
                tasks.append(task)
                await asyncio.sleep(0.1)
            await asyncio.gather(*tasks)


async def get_study_levels(session: ClientSession, alias: str) -> None:
    """
    Getting study levels
    :param session:
    :param alias:
    """
    url = f"{TT_API_URL}/study/divisions/{alias}/programs/levels"
    response = await request(session, url)
    for level in response:
        parsed_level = StudyLevel(**level)
        for program_combination in parsed_level.program_combinations:
            for admission_year in program_combination.admission_years:
                program_ids.append(admission_year.study_program_id)


async def collecting_program_ids() -> None:
    """Getting IDs of all programs"""
    study_divisions = await get_study_divisions()
    aliases = [division.alias for division in study_divisions]
    aliases_by_parts = list(chunks_generator(aliases, 4))
    await create_and_run_tasks(aliases_by_parts, get_study_levels)


async def get_groups(session: ClientSession, program_id: str) -> None:
    """
    Getting IDs and names of all groups of the study program
    :param session:
    :param program_id:
    """
    url = f"{TT_API_URL}/progams/{program_id}/groups"
    response = await request(session, url)
    if "Groups" in response:
        for group in response["Groups"]:
            if len(group) != 0:
                groups.append(GroupSearchInfo(tt_id=group["StudentGroupId"], name=group["StudentGroupName"]))
    else:
        remaining_program_ids.append(program_id)


def edit_env_variable(env_variable: str, old_value: str, new_value: str) -> None:
    """
    Changing the value of a variable in .env file
    :param env_variable:
    :param old_value:
    :param new_value:
    """
    with open(".env", "r", encoding="utf-8") as env_file:
        new_data = env_file.read().replace(f"{env_variable}={old_value}", f"{env_variable}={new_value}")
    with open(".env", "w", encoding="utf-8") as env_file:
        env_file.write(new_data)


async def adding_groups_to_db() -> None:
    """Adding all groups to the database"""
    logging.info("Collecting programs...")
    await collecting_program_ids()
    logging.info("Collecting groups...")
    while True:
        global program_ids
        program_ids_by_parts = list(chunks_generator(program_ids, 50))
        await create_and_run_tasks(program_ids_by_parts, get_groups)
        logging.info("Groups are gathering for the %s remaining programs...", len(remaining_program_ids))
        for group in groups:
            await database.add_new_group(group_tt_id=group.tt_id, group_name=group.name)
        if len(remaining_program_ids) == 0 or not program_ids:
            break
        program_ids = remaining_program_ids.copy()
        remaining_program_ids.clear()
    edit_env_variable("ARE_GROUPS_COLLECTED", "False", "True")
