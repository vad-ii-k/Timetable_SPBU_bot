from datetime import date, timedelta
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


async def teacher_timetable(teacher_id) -> str:
    current_date = date.today()
    monday = current_date - timedelta(days=current_date.weekday())
    sunday = monday + timedelta(days=5)
    url = f"https://timetable.spbu.ru/api/v1/educators/{teacher_id}/events/{monday}/{sunday}"
    response = await make_request(url)
    timetable = "<b>Преподаватель</b>  {}\n".format(response.get("EducatorDisplayText"))
    if len(response["EducatorEventsDays"]) > 0:
        for day in response["EducatorEventsDays"]:
            timetable += "\n<b>{}</b>\n".format(day.get("DayString"))
            events = day["DayStudyEvents"]
            for event in events:
                timetable += "  {}\n".format(event.get("TimeIntervalString"))
                timetable += "  <b>{}</b>\n".format(event.get("Subject"))
                timetable += "    {}\n".format(event.get("ContingentUnitName"))
                if event.get("LocationsDisplayText") == "С использованием информационно-коммуникационных технологий":
                    timetable += "    {}\n".format("С использованием ИКТ")
                else:
                    timetable += "    {}\n".format(event.get("LocationsDisplayText"))
    return timetable
