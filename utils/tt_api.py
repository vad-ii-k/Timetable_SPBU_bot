from datetime import date, timedelta
import aiohttp

from utils.image_converter.converter import TimetableIMG
from utils.timetable_parsers import teacher_timetable_parser_day, group_timetable_parser_day


async def request(url: str) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                return await resp.json()
            else:
                return {}

tt_api_url = "https://timetable.spbu.ru/api/v1"


async def teacher_search(last_name: str) -> list:
    url = tt_api_url + f"/educators/search/{last_name}"
    response = await request(url)
    teachers = []
    for teacher in response["Educators"]:
        teachers.append({"Id": teacher["Id"], "FullName": teacher["FullName"]})

    return teachers


async def calculator_of_days(day_counter: int) -> tuple:
    if day_counter > 0:
        current_date = date.today() + timedelta(day_counter)
    else:
        current_date = date.today() - timedelta(-day_counter)
    next_day = current_date + timedelta(days=1)
    return current_date, next_day


async def calculator_of_week_days(week_counter: int) -> tuple:
    current_date = date.today() + timedelta(week_counter * 7)
    monday = current_date - timedelta(days=current_date.weekday())
    sunday = monday + timedelta(days=6)
    return monday, sunday


async def teacher_timetable_day(teacher_id: int, day_counter=0) -> str:
    current_date, next_day = await calculator_of_days(day_counter)
    url = tt_api_url + f"/educators/{teacher_id}/events/{current_date}/{next_day}"
    response = await request(url)

    timetable = "Преподаватель: <b>{educator}</b>\n📆 <a href='{link}'>День: {current_date}</a> \n".format(
        educator=response.get("EducatorDisplayText"),
        link=f"https://timetable.spbu.ru/WeekEducatorEvents/{teacher_id}/{current_date}",
        current_date=current_date.strftime("%d.%m")
    )

    schedule_pic = TimetableIMG("utils/image_converter/output.png")
    schedule_pic.image_title(title=response.get("EducatorDisplayText"),
                             date=current_date.strftime("%A, %d %B"))

    if len(response["EducatorEventsDays"]) > 0:
        day_timetable = await teacher_timetable_parser_day(response["EducatorEventsDays"][0])
        schedule_pic.insert_timetable(timetable=day_timetable)
    else:
        day_timetable = '\n<i>Занятий в этот день нет</i>'
    timetable += day_timetable
    schedule_pic.crop_image()
    return timetable


async def teacher_timetable_week(teacher_id: int, week_counter=0) -> str:
    monday, sunday = await calculator_of_week_days(week_counter)
    url = tt_api_url + f"/educators/{teacher_id}/events/{monday}/{sunday}"
    response = await request(url)

    timetable = "Преподаватель: <b>{educator}</b>\n📆 <a href='{link}'>Неделя: {monday} — {sunday}</a>\n".format(
        educator=response.get("EducatorDisplayText"),
        link=f"https://timetable.spbu.ru/WeekEducatorEvents/{teacher_id}/{monday}",
        monday=monday.strftime("%d.%m"),
        sunday=sunday.strftime("%d.%m")
    )

    schedule_pic = TimetableIMG("utils/image_converter/output.png")
    schedule_pic.image_title(title=response.get("EducatorDisplayText"),
                             date="Неделя: {monday} — {sunday}".format(
                                 monday=monday.strftime("%d.%m"),
                                 sunday=sunday.strftime("%d.%m")))

    if len(response["EducatorEventsDays"]) > 0:
        for day in response["EducatorEventsDays"]:
            day_timetable = await teacher_timetable_parser_day(day)
            timetable += day_timetable
            schedule_pic.insert_timetable(timetable=day_timetable)
    else:
        timetable += '\n<i>Занятий на этой неделе нет</i>'
    schedule_pic.crop_image()
    return timetable


async def group_timetable_day(group_id: int, day_counter=0) -> str:
    current_date, next_day = await calculator_of_days(day_counter)
    url = tt_api_url + f"/groups/{group_id}/events/{current_date}/{next_day}"
    response = await request(url)

    timetable = "<b>{group}</b>\n📆 <a href='{link}'>День: {current_date}</a>\n".format(
        group=response.get("StudentGroupDisplayName"),
        link=f"https://timetable.spbu.ru/MATH/StudentGroupEvents/Primary/{group_id}/{current_date}",
        current_date=current_date.strftime("%d.%m")
    )

    schedule_pic = TimetableIMG("utils/image_converter/output.png")
    schedule_pic.image_title(title=response.get("StudentGroupDisplayName"),
                             date=current_date.strftime("%A, %d %B"))

    if len(response["Days"]) > 0:
        day_timetable = await group_timetable_parser_day(response["Days"][0])
        schedule_pic.insert_timetable(timetable=day_timetable)
    else:
        day_timetable = '\n<i>Занятий в этот день нет</i>'
    timetable += day_timetable
    schedule_pic.crop_image()
    return timetable


async def group_timetable_week(group_id: int, week_counter=0) -> str:
    monday, sunday = await calculator_of_week_days(week_counter)
    url = tt_api_url + f"/groups/{group_id}/events/{monday}/{sunday}"
    response = await request(url)

    timetable = "<b>{group}</b>\n📆 <a href='{link}'>Неделя: {monday} — {sunday}</a>\n".format(
        group=response.get("StudentGroupDisplayName"),
        link=f"https://timetable.spbu.ru/MATH/StudentGroupEvents/Primary/{group_id}/{monday}",
        monday=monday.strftime("%d.%m"),
        sunday=sunday.strftime("%d.%m")
    )
    schedule_pic = TimetableIMG("utils/image_converter/output.png")
    schedule_pic.image_title(title=response.get("StudentGroupDisplayName"),
                             date="Неделя: {monday} — {sunday}".format(
                                 monday=monday.strftime("%d.%m"),
                                 sunday=sunday.strftime("%d.%m")))

    if len(response["Days"]) > 0:
        for day in response["Days"]:
            day_timetable = await group_timetable_parser_day(day)
            if len(timetable) + len(day_timetable) < 4000:
                timetable += day_timetable
            else:
                timetable += "\n\nСообщение слишком длинное..."
                break
            schedule_pic.insert_timetable(timetable=day_timetable)
    else:
        timetable += '\n<i>Занятий в этот день нет</i>'
    schedule_pic.crop_image()
    return timetable


async def get_study_divisions() -> list:
    url = tt_api_url + "/study/divisions"
    response = await request(url)

    study_divisions = []
    for division in response:
        study_divisions.append({"Alias": division["Alias"], "Name": division["Name"]})

    return study_divisions


async def get_study_levels(alias: str) -> tuple:
    url = tt_api_url + f"/study/divisions/{alias}/programs/levels"
    response = await request(url)

    study_levels = []
    for serial, level in enumerate(response):
        study_levels.append({"StudyLevelName": level["StudyLevelName"], "Serial": serial})
    return study_levels, response


async def get_groups(program_id: str) -> list:
    url = tt_api_url + f"/progams/{program_id}/groups"
    response = await request(url)

    groups = []
    for group in response["Groups"]:
        groups.append({"StudentGroupId": group["StudentGroupId"], "StudentGroupName": group["StudentGroupName"]})
    return groups
