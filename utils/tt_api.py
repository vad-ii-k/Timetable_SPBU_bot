from datetime import date, timedelta
import aiohttp

from utils.timetable_parsers import teacher_timetable_parser


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


async def teacher_timetable_week(teacher_id) -> str:
    current_date = date.today()
    monday = current_date - timedelta(days=current_date.weekday())
    sunday = monday + timedelta(days=6)
    url = f"https://timetable.spbu.ru/api/v1/educators/{teacher_id}/events/{monday}/{sunday}"
    response = await make_request(url)
    timetable = await teacher_timetable_parser(response)
    return timetable
