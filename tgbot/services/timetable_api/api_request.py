""" Timetable API request """

import asyncio
import logging
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from random import shuffle

from aiogram.client.session import aiohttp
from aiohttp import ClientResponse, ClientSession
from aiohttp_socks import ProxyConnector, ProxyError

from tgbot.config import app_config


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


async def request(url: str) -> dict:
    """

    :param url:
    :return:
    """
    shuffle(app_config.proxy.ips)
    # Iterating through the proxy until we get the OK status
    for proxy_ip in app_config.proxy.ips:
        connector = ProxyConnector.from_url(f"HTTP://{app_config.proxy.login}:{app_config.proxy.password}@{proxy_ip}")
        async with ClientSession(connector=connector) as session:
            try:
                async with session.get(url, timeout=5) as resp:
                    if resp.status == 200:
                        return await resp.json()
            except ProxyError:
                break
            except asyncio.exceptions.TimeoutError:
                break
    async with aiohttp.ClientSession() as session:
        # TT API (LETT/programs/levels) на проде отвечает дольше 30 с
        for attempt in range(4):
            async with session.get(url, timeout=60) as resp:
                if resp.status == 200:
                    return await resp.json()
                if resp.status != 429:
                    break
                wait = retry_after_seconds(resp)
                logging.warning("TT API 429, пауза %s с: %s headers=%s", wait, url, dict(resp.headers))
                if not wait or attempt >= 3:
                    break
                await asyncio.sleep(wait)
    return {}
