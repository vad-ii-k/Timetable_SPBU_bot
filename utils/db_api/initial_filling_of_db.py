import asyncio
import os
import random

import aiohttp
from aiohttp_socks import ProxyConnector

from data.config import PROXY_IPS, PROXY_LOGIN, PROXY_PASSWORD
from loader import db
from utils.timetable.api import tt_api_url


async def get_proxy_connector() -> ProxyConnector:
    ip = PROXY_IPS[random.randint(0, 100) % len(PROXY_IPS)]
    connector = ProxyConnector.from_url(f'HTTP://{PROXY_LOGIN}:{PROXY_PASSWORD}@{ip}')
    return connector


async def request(session: aiohttp.ClientSession, url: str) -> dict:
    async with session.get(url) as response:
        print(url)
        if response.status == 200:
            return await response.json()
        else:
            print(response.status)
            return {}


async def get_study_divisions() -> list:
    url = tt_api_url + "/study/divisions"
    async with aiohttp.ClientSession() as session:
        response = await request(session, url)

    study_divisions = []
    for division in response:
        study_divisions.append({"Alias": division["Alias"], "Name": division["Name"]})
    return study_divisions

program_ids = []


async def collecting_program_ids():
    aliases = [item['Alias'] for item in (await get_study_divisions())]
    connector = await get_proxy_connector()
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        for alias in aliases:
            task = asyncio.create_task(get_study_levels(session, alias))
            tasks.append(task)
        await asyncio.gather(*tasks)


async def get_study_levels(session: aiohttp.ClientSession, alias: str):
    url = tt_api_url + f"/study/divisions/{alias}/programs/levels"
    response = await request(session, url)
    for level in response:
        program_combinations = level['StudyProgramCombinations']
        for program_combination in program_combinations:
            years = program_combination['AdmissionYears']
            for year in years:
                program_ids.append(str(year['StudyProgramId']))

groups = []
remaining_program_ids = []


async def get_groups(session: aiohttp.ClientSession, program_id: str):
    url = tt_api_url + f"/progams/{program_id}/groups"
    response = await request(session, url)
    try:
        for group in response["Groups"]:
            if len(group) != 0:
                groups.append({"GroupId": group["StudentGroupId"], "GroupName": group["StudentGroupName"]})
    except KeyError:
        remaining_program_ids.append(program_id)


def chunks_generator(lst: list, chuck_size: int):
    for i in range(0, len(lst), chuck_size):
        yield lst[i: i + chuck_size]


async def collecting_groups_info():
    program_ids_by_parts = list(chunks_generator(program_ids, 400))
    for chunk in program_ids_by_parts:
        connector = await get_proxy_connector()
        async with aiohttp.ClientSession(connector=connector) as session:
            tasks = []
            for program_id in chunk:
                task = asyncio.create_task(get_groups(session, program_id))
                tasks.append(task)
                await asyncio.sleep(0.06)
            await asyncio.gather(*tasks)


async def adding_groups_to_db():
    with open("data/program_ids.txt", 'r+') as file:
        global program_ids
        file_size = os.stat(file.name).st_size
        if file_size == 0:
            await collecting_program_ids()
        elif file_size != 1:
            [program_ids.append(program_id) for program_id in file.readline().split(' ')]
    if file_size != 1:
        await collecting_groups_info()
        for group in groups:
            await db.add_new_group(tt_id=group["GroupId"], group_name=group["GroupName"])

        with open("data/program_ids.txt", 'w') as file:
            str_to_write = ''.join([program_id + ' ' for program_id in remaining_program_ids])
            file.write(str_to_write[:-1])
            if len(remaining_program_ids) == 0:
                file.write(' ')
