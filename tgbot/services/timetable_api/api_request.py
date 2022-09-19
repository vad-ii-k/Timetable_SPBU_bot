from random import shuffle

from aiogram.client.session import aiohttp
from aiohttp import ClientSession
from aiohttp_socks import ProxyConnector, ProxyError


async def request(url: str) -> dict:
    from bot import config
    shuffle(config.proxy.ips)
    # Iterating through the proxy until we get the OK status
    for proxy_ip in config.proxy.ips:
        connector = ProxyConnector.from_url(f'HTTP://{config.proxy.login}:{config.proxy.password}@{proxy_ip}')
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
