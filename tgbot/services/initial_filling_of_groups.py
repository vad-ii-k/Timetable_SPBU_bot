""" Initial filling of groups for searching by name """

import asyncio
import logging
from pathlib import Path
from typing import Callable, Coroutine

from aiohttp import ClientError, ClientSession, ClientTimeout
from aiohttp_socks import ProxyConnectionError, ProxyConnector, ProxyError

from tgbot.config import app_config
from tgbot.services.db_api.db_commands import database
from tgbot.services.schedule.data_classes import GroupSearchInfo, StudyLevel
from tgbot.services.timetable_api.api_request import wait_after_429
from tgbot.services.timetable_api.timetable_api import TT_API_URL, get_study_divisions

logger = logging.getLogger(__name__)

program_ids: list[str] = []
groups: list[GroupSearchInfo] = []

_REQUEST_ATTEMPTS = 10
_REQUEST_TIMEOUT = ClientTimeout(total=60)
_REQUEST_PAUSE = 1.0
# Фон: лучше подождать лимит TT API, чем пропустить программу
_MAX_429_WAIT = 300.0


async def request(session: ClientSession, url: str) -> dict | None:
    """
    Request to API with [ClientSession](https://docs.aiohttp.org/en/stable/client_reference.html)
    :param session:
    :param url:
    :return: JSON или None, если запрос окончательно не удался
    """
    for attempt in range(1, _REQUEST_ATTEMPTS + 1):
        try:
            async with session.get(url, timeout=_REQUEST_TIMEOUT) as response:
                if response.status == 200:
                    return await response.json()
                if response.status == 429:
                    wait = wait_after_429(response, attempt, max_wait=_MAX_429_WAIT)
                    logger.warning("TT API 429, пауза %s с (попытка %s/%s): %s", wait, attempt, _REQUEST_ATTEMPTS, url)
                    if attempt >= _REQUEST_ATTEMPTS:
                        break
                    await asyncio.sleep(wait)
                    continue
                logger.warning("TT API %s: %s", response.status, url)
                if response.status == 404:
                    return {"Groups": []}
                if response.status < 500:
                    return {}
        except (ProxyError, ProxyConnectionError, TimeoutError, ClientError) as err:
            logger.warning(
                "TT API request failed (попытка %s/%s, %s): %s",
                attempt,
                _REQUEST_ATTEMPTS,
                url,
                str(err) or type(err).__name__,
            )
        if attempt < _REQUEST_ATTEMPTS:
            await asyncio.sleep(min(attempt * 2, _MAX_429_WAIT))
    logger.error("TT API request failed after %s attempts (%s)", _REQUEST_ATTEMPTS, url)
    return None


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
                logger.exception("Task failed for %s", item)
            await asyncio.sleep(_REQUEST_PAUSE)


async def get_study_levels(session: ClientSession, alias: str) -> None:
    """
    Getting study levels
    :param session:
    :param alias:
    """
    url = f"{TT_API_URL}/study/divisions/{alias}/programs/levels"
    response = await request(session, url)
    if not isinstance(response, list):
        logger.warning("Skip study levels for %s", alias)
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
    logger.info("Collecting programs for %d divisions", len(aliases))
    await create_and_run_tasks(aliases, get_study_levels)


async def get_groups(session: ClientSession, program_id: str) -> None:
    """
    Getting IDs and names of all groups of the study program
    :param session:
    :param program_id:
    """
    url = f"{TT_API_URL}/programs/{program_id}/groups"
    response = await request(session, url)
    if response is None:
        logger.warning("Не удалось получить группы программы %s (лимит/сеть)", program_id)
        return
    if "Groups" not in response:
        logger.warning("No groups for program %s", program_id)
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
        logger.warning(
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
    logger.info("Saving %d groups to database", len(groups))
    for group in groups:
        await database.add_new_group(group_tt_id=group.tt_id, group_name=group.name)
    groups.clear()


async def adding_groups_to_db() -> None:
    """Adding all groups to the database"""
    try:
        logger.info("Collecting programs in background...")
        await collecting_program_ids()
        logger.info("Collected %d program IDs", len(program_ids))

        logger.info("Collecting groups...")
        await create_and_run_tasks(program_ids, get_groups)
        await _save_groups()

        edit_env_variable("ARE_GROUPS_COLLECTED", "False", "True")
        logger.info("Finished adding groups to the database.")
    except Exception:
        logger.exception("Initial group filling failed")
