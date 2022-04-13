import asyncio
import aiohttp

from loader import db
from utils.tt_api import tt_api_url


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
    async with aiohttp.ClientSession() as session:
        tasks = []
        for alias in aliases:
            task = asyncio.create_task(get_study_levels(session, alias))
            tasks.append(task)
        await asyncio.gather(*tasks)


async def get_study_levels(session: aiohttp.ClientSession, alias: str):
    url = tt_api_url + f"/study/divisions/{alias}/programs/levels"
    response = await request(session, url)
    for level in response:
        program_combinatons = level['StudyProgramCombinations']
        for program_combinaton in program_combinatons:
            years = program_combinaton['AdmissionYears']
            for year in years:
                program_ids.append(year['StudyProgramId'])

groups = []


async def get_groups(session: aiohttp.ClientSession, program_id: str):
    url = tt_api_url + f"/progams/{program_id}/groups"
    response = await request(session, url)
    if response.get("Groups"):
        for group in response["Groups"]:
            if len(group) != 0:
                groups.append({"GroupId": group["StudentGroupId"], "GroupName": group["StudentGroupName"]})


async def collecting_groups_info():
    async with aiohttp.ClientSession() as session:
        tasks = []
        for program_id in program_ids:
            task = asyncio.create_task(get_groups(session, program_id))
            tasks.append(task)
            await asyncio.sleep(0.1)
        await asyncio.gather(*tasks)


async def adding_groups_to_db():
    await collecting_program_ids()
    await collecting_groups_info()
    for group in groups:
        await db.add_new_group(tt_id=group["GroupId"], group_name=group["GroupName"])
