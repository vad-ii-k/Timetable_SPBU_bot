""" Timetable API request """

import asyncio
import logging
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from random import shuffle

from aiogram.client.session import aiohttp
from aiohttp import ClientError, ClientResponse, ClientSession, ClientTimeout
from aiohttp_socks import ProxyConnector, ProxyError

from tgbot.config import app_config

logger = logging.getLogger(__name__)

# LETT /programs/levels на проде часто отвечает дольше 45 с
_TT_TIMEOUT = ClientTimeout(total=90, sock_connect=15)
_MAX_429_WAIT = 60.0


class TimetableApiError(Exception):
    """TT API не вернул пригодный ответ (сеть, 429, пустое тело)."""


def retry_after_seconds(response: ClientResponse) -> float | None:
    """Секунды из стандартного заголовка Retry-After (RFC 9110)."""
    raw = response.headers.get("Retry-After")
    if raw is None:
        return None
    try:
        return max(0.0, float(raw))
    except ValueError:
        pass
    try:
        when = parsedate_to_datetime(raw)
    except (TypeError, ValueError, OverflowError):
        return None
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)
    return max(0.0, (when - datetime.now(timezone.utc)).total_seconds())


def wait_after_429(
    response: ClientResponse,
    attempt: int,
    max_wait: float = _MAX_429_WAIT,
) -> float:
    """Пауза после 429: Retry-After или экспонента, не больше max_wait."""
    header_wait = retry_after_seconds(response)
    if header_wait and header_wait > 0:
        return min(header_wait, max_wait)
    return min(2.0**attempt, max_wait)


async def request(url: str) -> dict | list:
    """
    Запрос к timetable.spbu.ru: прокси, затем прямой доступ с повторами на 429.
    :param url:
    :return: JSON или пустой dict при неуспехе
    """
    shuffle(app_config.proxy.ips)
    for proxy_ip in app_config.proxy.ips:
        connector = ProxyConnector.from_url(f"HTTP://{app_config.proxy.login}:{app_config.proxy.password}@{proxy_ip}")
        async with ClientSession(connector=connector) as session:
            try:
                async with session.get(url, timeout=ClientTimeout(total=5)) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    logger.debug("TT API через прокси %s: HTTP %s %s", proxy_ip, resp.status, url)
            except (ProxyError, TimeoutError, ClientError) as err:
                logger.debug("TT API прокси %s: %s", proxy_ip, err)
                break
    async with aiohttp.ClientSession() as session:
        last_status: int | None = None
        for attempt in range(3):
            try:
                async with session.get(url, timeout=_TT_TIMEOUT) as resp:
                    last_status = resp.status
                    if resp.status == 200:
                        return await resp.json()
                    if resp.status != 429:
                        logger.warning("TT API HTTP %s: %s", resp.status, url)
                        break
                    wait = wait_after_429(resp, attempt + 1)
                    logger.warning("TT API 429, пауза %s с: %s", wait, url)
                    if attempt >= 2:
                        break
                    await asyncio.sleep(wait)
            except (TimeoutError, ClientError) as err:
                logger.warning("TT API сбой (%s): %s", url, str(err) or type(err).__name__)
                break
    logger.error("TT API недоступен (%s), last_status=%s", url, last_status)
    return {}
