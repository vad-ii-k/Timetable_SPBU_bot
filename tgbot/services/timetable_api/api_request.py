from random import shuffle

from aiogram.client.session import aiohttp
from aiohttp_client_cache import RedisBackend, CachedSession
from aiohttp_socks import ProxyConnector, ProxyError

from tgbot.config import config


def get_cache(expire_after: int) -> RedisBackend:
    redis_cache = RedisBackend(
        cache_name='aiohttp-cache',
        address=f'redis://{config.redis.host}',
        port=config.redis.port,
        password=config.redis.password,
        db=2,
        expire_after=expire_after,
    )
    return redis_cache


async def request(url: str, expire_after: int = 60) -> dict:
    shuffle(config.proxy.ips)
    # Iterating through the proxy until we get the OK status
    for proxy_ip in config.proxy.ips:
        connector = ProxyConnector.from_url(f'HTTP://{config.proxy.login}:{config.proxy.password}@{proxy_ip}')
        async with CachedSession(cache=get_cache(expire_after=expire_after), connector=connector) as session:
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
