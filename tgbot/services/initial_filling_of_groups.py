""" Initial filling of groups for searching by name """

import asyncio
import logging
from typing import Callable, Coroutine

from aiohttp import ClientError, ClientSession
from aiohttp_socks import ProxyConnectionError, ProxyConnector, ProxyError

from tgbot.config import app_config
from tgbot.services.db_api.db_commands import database
from tgbot.services.schedule.data_classes import GroupSearchInfo, StudyLevel
from tgbot.services.timetable_api.timetable_api import TT_API_URL, get_study_divisions

program_ids: list[str] = []
groups: list[GroupSearchInfo] = []
remaining_program_ids: list[str] = []

_CONCURRENCY = 8


async def request(session: ClientSession, url: str) -> dict:
    """
    Request to API with [ClientSession](https://docs.aiohttp.org/en/stable/client_reference.html)
    :param session:
    :param url:
    :return:
    """
    try:
        async with session.get(url, timeout=15) as response:
            if response.status == 200:
                return await response.json()
            logging.warning("TT API %s: %s", response.status, url)
            if response.status == 404:
                return {"Groups": []}
    except (ProxyError, ProxyConnectionError, TimeoutError, ClientError) as err:
        logging.error("TT API request failed (%s): %s", url, err)
    return {}


async def create_and_run_tasks(items: list[str], function: Callable[[ClientSession, str], Coroutine]) -> None:
    """Параллельные запросы к API с ограничением одновременных соединений"""
    connector = None
    if app_config.proxy.ips:
        connector = ProxyConnector.from_url(
            f"HTTP://{app_config.proxy.login}:{app_config.proxy.password}@{app_config.proxy.ips[0]}"
        )
    semaphore = asyncio.Semaphore(_CONCURRENCY)

    async with ClientSession(connector=connector) as session:

        async def run_one(item: str) -> None:
            async with semaphore:
                await function(session, item)

        results = await asyncio.gather(*(run_one(item) for item in items), return_exceptions=True)

    for item, result in zip(items, results):
        if isinstance(result, Exception):
            logging.error("Task failed for %s: %s", item, result)


async def get_study_levels(session: ClientSession, alias: str) -> None:
    """
    Getting study levels
    :param session:
    :param alias:
    """
    url = f"{TT_API_URL}/study/divisions/{alias}/programs/levels"
    response = await request(session, url)
    if not isinstance(response, list):
        logging.warning("Skip study levels for %s", alias)
        return
    for level in response:
        parsed_level = StudyLevel(**level)
        for program_combination in parsed_level.program_combinations:
            for admission_year in program_combination.admission_years:
                program_ids.append(str(admission_year.study_program_id))


async def collecting_program_ids() -> None:
    """Getting IDs of all programs"""
    study_divisions = await get_study_divisions()
    aliases = [division.alias for division in study_divisions]
    logging.info("Collecting programs for %d divisions", len(aliases))
    await create_and_run_tasks(aliases, get_study_levels)


async def get_groups(session: ClientSession, program_id: str) -> None:
    """
    Getting IDs and names of all groups of the study program
    :param session:
    :param program_id:
    """
    url = f"{TT_API_URL}/programs/{program_id}/groups"
    response = await request(session, url)
    if "Groups" in response:
        for group in response["Groups"]:
            if len(group) != 0:
                groups.append(GroupSearchInfo(tt_id=group["StudentGroupId"], name=group["StudentGroupName"]))
        return
    logging.warning("Retry program %s later", program_id)
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


async def _save_groups() -> None:
    logging.info("Saving %d groups to database", len(groups))
    for group in groups:
        await database.add_new_group(group_tt_id=group.tt_id, group_name=group.name)
    groups.clear()


async def adding_groups_to_db() -> None:
    """Adding all groups to the database"""
    logging.info("Collecting programs...")
    await collecting_program_ids()
    logging.info("Collected %d program IDs", len(program_ids))

    logging.info("Collecting groups...")
    await create_and_run_tasks(program_ids, get_groups)
    await _save_groups()

    if remaining_program_ids:
        retry_ids = remaining_program_ids.copy()
        remaining_program_ids.clear()
        logging.info("Retry %d programs once", len(retry_ids))
        await create_and_run_tasks(retry_ids, get_groups)
        await _save_groups()
        if remaining_program_ids:
            logging.warning("Skipped %d programs after retry", len(remaining_program_ids))

    edit_env_variable("ARE_GROUPS_COLLECTED", "False", "True")
    logging.info("Finished adding groups to the database.")
