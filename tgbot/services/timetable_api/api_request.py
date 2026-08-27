""" Timetable API request """

import asyncio
from random import shuffle

from aiogram.client.session import aiohttp
from aiohttp import ClientSession
from aiohttp_socks import ProxyConnector, ProxyError

from tgbot.config import app_config


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
    delay = 1
    async with aiohttp.ClientSession() as session:
        # TT API (LETT/programs/levels) на проде отвечает дольше 30 с
        for attempt in range(4):
            async with session.get(url, timeout=60) as resp:
                if resp.status == 200:
                    return await resp.json()
                if resp.status != 429:
                    break
                delay = min(delay * 2, 32)
                if attempt < 3:
                    await asyncio.sleep(delay)
    return {}
