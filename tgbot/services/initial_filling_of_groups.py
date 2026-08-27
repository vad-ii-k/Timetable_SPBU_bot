""" Initial filling of groups for searching by name """

import asyncio
import logging
from pathlib import Path
from typing import Callable, Coroutine

from aiohttp import ClientError, ClientSession
from aiohttp_socks import ProxyConnectionError, ProxyConnector, ProxyError

from tgbot.config import app_config
from tgbot.services.db_api.db_commands import database
from tgbot.services.schedule.data_classes import GroupSearchInfo, StudyLevel
from tgbot.services.timetable_api.timetable_api import TT_API_URL, get_study_divisions

program_ids: list[str] = []
groups: list[GroupSearchInfo] = []

_REQUEST_ATTEMPTS = 6
_REQUEST_TIMEOUT = 60
_REQUEST_PAUSE = 1.0
_RATE_DELAY_MAX = 60
_rate_delay = _REQUEST_PAUSE


async def request(session: ClientSession, url: str) -> dict:
    """
    Request to API with [ClientSession](https://docs.aiohttp.org/en/stable/client_reference.html)
    :param session:
    :param url:
    :return:
    """
    global _rate_delay
    for attempt in range(1, _REQUEST_ATTEMPTS + 1):
        try:
            async with session.get(url, timeout=_REQUEST_TIMEOUT) as response:
                if response.status == 200:
                    _rate_delay = max(_REQUEST_PAUSE, _rate_delay / 2)
                    return await response.json()
                if response.status == 429:
                    _rate_delay = min(_rate_delay * 2, _RATE_DELAY_MAX)
                    logging.warning("TT API 429, пауза %s с: %s", _rate_delay, url)
                    if attempt < _REQUEST_ATTEMPTS:
                        await asyncio.sleep(_rate_delay)
                    continue
                logging.warning("TT API %s: %s", response.status, url)
                if response.status == 404:
                    return {"Groups": []}
                if response.status < 500:
                    return {}
        except (ProxyError, ProxyConnectionError, TimeoutError, ClientError) as err:
            logging.warning(
                "TT API request failed (попытка %s/%s, %s): %s",
                attempt,
                _REQUEST_ATTEMPTS,
                url,
                str(err) or type(err).__name__,
            )
        if attempt < _REQUEST_ATTEMPTS:
            await asyncio.sleep(attempt * 2)
    logging.error("TT API request failed after %s attempts (%s)", _REQUEST_ATTEMPTS, url)
    return {}


async def create_and_run_tasks(items: list[str], function: Callable[[ClientSession, str], Coroutine]) -> None:
    """Последовательные запросы к API с паузой, чтобы не нагружать timetable."""
    connector = None
    if app_config.proxy.ips:
        connector = ProxyConnector.from_url(
            f"HTTP://{app_config.proxy.login}:{app_config.proxy.password}@{app_config.proxy.ips[0]}"
        )
    async with ClientSession(connector=connector) as session:
        for item in items:
            try:
                await function(session, item)
            except Exception:
                logging.exception("Task failed for %s", item)
            await asyncio.sleep(_rate_delay)


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
    if "Groups" not in response:
        logging.warning("No groups for program %s", program_id)
        return
    for group in response["Groups"]:
        if group:
            groups.append(GroupSearchInfo(tt_id=group["StudentGroupId"], name=group["StudentGroupName"]))


def edit_env_variable(env_variable: str, old_value: str, new_value: str) -> None:
    """
    Changing the value of a variable in .env file
    :param env_variable:
    :param old_value:
    :param new_value:
    """
    env_path = Path(".env")
    if not env_path.is_file():
        logging.warning(
            "Файла .env нет в контейнере — выставьте %s=%s в env_file на хосте, "
            "иначе сбор групп запустится снова",
            env_variable,
            new_value,
        )
        return
    new_data = env_path.read_text(encoding="utf-8").replace(
        f"{env_variable}={old_value}", f"{env_variable}={new_value}"
    )
    env_path.write_text(new_data, encoding="utf-8")


async def _save_groups() -> None:
    logging.info("Saving %d groups to database", len(groups))
    for group in groups:
        await database.add_new_group(group_tt_id=group.tt_id, group_name=group.name)
    groups.clear()


async def adding_groups_to_db() -> None:
    """Adding all groups to the database"""
    try:
        logging.info("Collecting programs in background...")
        await collecting_program_ids()
        logging.info("Collected %d program IDs", len(program_ids))

        logging.info("Collecting groups...")
        await create_and_run_tasks(program_ids, get_groups)
        await _save_groups()

        edit_env_variable("ARE_GROUPS_COLLECTED", "False", "True")
        logging.info("Finished adding groups to the database.")
    except Exception:
        logging.exception("Initial group filling failed")
