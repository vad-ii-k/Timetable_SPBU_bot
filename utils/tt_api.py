from datetime import date, timedelta
import aiohttp

from utils.timetable_parsers import teacher_timetable_parser_day


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


async def teacher_timetable_day(teacher_id, day_counter=0) -> str:
    if day_counter > 0:
        current_date = date.today() + timedelta(day_counter)
    else:
        current_date = date.today() - timedelta(-day_counter)
    next_day = current_date + timedelta(days=1)
    url = f"https://timetable.spbu.ru/api/v1/educators/{teacher_id}/events/{current_date}/{next_day}"
    response = await make_request(url)

    timetable = "Преподаватель: <b>{educator}</b>\n<a href='{link}'>День: {current_date}</a> \n".format(
        educator=response.get("EducatorDisplayText"),
        link=f"https://timetable.spbu.ru/WeekEducatorEvents/{teacher_id}/{current_date}",
        current_date=current_date.strftime("%d.%m")
    )

    if len(response["EducatorEventsDays"]) > 0:
        timetable += await teacher_timetable_parser_day(response["EducatorEventsDays"][0])
    else:
        timetable += '\n<i>Занятий в этот день нет</i>'
    return timetable


async def teacher_timetable_week(teacher_id, week_counter=0) -> str:
    current_date = date.today() + timedelta(week_counter * 7)
    monday = current_date - timedelta(days=current_date.weekday())
    sunday = monday + timedelta(days=6)
    url = f"https://timetable.spbu.ru/api/v1/educators/{teacher_id}/events/{monday}/{sunday}"
    response = await make_request(url)

    timetable = "Преподаватель: <b>{educator}</b>\n<a href='{link}'>Неделя: {monday} — {sunday}</a> \n".format(
        educator=response.get("EducatorDisplayText"),
        link=f"https://timetable.spbu.ru/WeekEducatorEvents/{teacher_id}/{monday}",
        monday=monday.strftime("%d.%m"),
        sunday=sunday.strftime("%d.%m")
    )

    if len(response["EducatorEventsDays"]) > 0:
        for day in response["EducatorEventsDays"]:
            timetable += await teacher_timetable_parser_day(day)
    else:
        timetable += '\n<i>Занятий на этой неделе нет</i>'
    return timetable
