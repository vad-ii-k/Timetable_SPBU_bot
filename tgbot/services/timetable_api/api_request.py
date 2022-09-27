from random import shuffle

from aiogram.client.session import aiohttp
from aiohttp import ClientSession
from aiohttp_client_cache import RedisBackend
from aiohttp_socks import ProxyConnector, ProxyError

from tgbot.config import app_config


def get_cache(expire_after: int) -> RedisBackend:
    redis_cache = RedisBackend(
        cache_name='aiohttp-cache',
        address=f'redis://{app_config.redis.host}',
        port=app_config.redis.port,
        password=app_config.redis.password,
        db=2,
        expire_after=expire_after,
    )
    return redis_cache


async def request(url: str, expire_after: int = 60) -> dict:
    shuffle(app_config.proxy.ips)
    # Iterating through the proxy until we get the OK status
    for proxy_ip in app_config.proxy.ips:
        connector = ProxyConnector.from_url(f'HTTP://{app_config.proxy.login}:{app_config.proxy.password}@{proxy_ip}')
        # async with CachedSession(cache=get_cache(expire_after=expire_after), connector=connector) as session:
        async with ClientSession(connector=connector) as session:
            try:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        return await resp.json()
            except ProxyError:
                break
    # Trying to get a response without a proxy
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                return await resp.json()
    return {}
