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
    # Trying to get a response without a proxy
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                return await resp.json()
    return {}
