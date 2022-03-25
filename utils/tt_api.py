import asyncio

import aiohttp


async def make_request(url) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                return await resp.json()


async def teacher_search(last_name) -> list:
    url = f"https://timetable.spbu.ru/api/v1/educators/search/{last_name}"
    response = await make_request(url)
    teachers = []
    for teacher in response["Educators"]:
        teachers.append({"Id": teacher["Id"], "FullName": teacher["FullName"]})

    return teachers
