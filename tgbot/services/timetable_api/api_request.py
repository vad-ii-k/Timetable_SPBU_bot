""" Timetable API request """
import asyncio
from datetime import timedelta
from random import shuffle

from aiogram.client.session import aiohttp
from aiohttp_client_cache import RedisBackend, CachedSession
from aiohttp_socks import ProxyConnector, ProxyError

from tgbot.config import app_config


def _get_cache(expire_after_days: float) -> RedisBackend:
    """

    :param expire_after_days:
    :return:
    """
    redis_cache = RedisBackend(
        cache_name='aiohttp-cache',
        address=f'redis://{app_config.redis.host}',
        port=app_config.redis.port,
        password=app_config.redis.password,
        db=2,
        expire_after=timedelta(days=expire_after_days),
    )
    return redis_cache


async def request(url: str, expire_after_days: float = 0.1) -> dict:
    """

    :param url:
    :param expire_after_days:
    :return:
    """
    shuffle(app_config.proxy.ips)
    # Iterating through the proxy until we get the OK status
    for proxy_ip in app_config.proxy.ips:
        connector = ProxyConnector.from_url(f'HTTP://{app_config.proxy.login}:{app_config.proxy.password}@{proxy_ip}')
        async with CachedSession(cache=_get_cache(expire_after_days=expire_after_days), connector=connector) as session:
            try:
                async with session.get(url, timeout=3) as resp:
                    if resp.status == 200:
                        return await resp.json()
            except ProxyError:
                continue
            except asyncio.exceptions.TimeoutError:
                break
    # Trying to get a response without a proxy
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                return await resp.json()
    return {}
