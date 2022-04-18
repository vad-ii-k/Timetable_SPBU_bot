import aiohttp

from utils.db_api.db_timetable import add_group_timetable_to_db
from utils.image_converter.converter import TimetableIMG
from utils.timetable.helpers import calculator_of_days, calculator_of_week_days
from utils.timetable.parsers import teacher_timetable_parser_day, teacher_timetable_week_header, \
    teacher_timetable_day_header


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


async def get_teacher_timetable_day(teacher_id: int, day_counter=0) -> str:
    current_date, next_day = await calculator_of_days(day_counter)
    url = tt_api_url + f"/educators/{teacher_id}/events/{current_date}/{next_day}"
    response = await request(url)

    timetable = await teacher_timetable_day_header(teacher_id, current_date, response)

    schedule_pic = TimetableIMG("utils/image_converter/output.png")
    schedule_pic.image_title(title=response.get("EducatorDisplayText"),
                             date=current_date.strftime("%A, %d %B"))

    if len(response["EducatorEventsDays"]) > 0:
        day_timetable = await teacher_timetable_parser_day(response["EducatorEventsDays"][0])
        schedule_pic.insert_timetable(timetable=day_timetable)
    else:
        day_timetable = '\n🏖 <i>Занятий в этот день нет</i>'
    timetable += day_timetable
    schedule_pic.crop_image()
    return timetable


async def get_teacher_timetable_week(teacher_id: int, week_counter=0) -> str:
    monday, sunday = await calculator_of_week_days(week_counter)
    url = tt_api_url + f"/educators/{teacher_id}/events/{monday}/{sunday}"
    response = await request(url)

    timetable = await teacher_timetable_week_header(teacher_id, monday, sunday, response)

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
        timetable += '\n🏖 <i>Занятий на этой неделе нет</i>'
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


async def fill_group_timetable_from_tt(group_id: int):
    monday, sunday = await calculator_of_week_days(week_counter=-1)
    url = tt_api_url + f"/groups/{group_id}/events/{monday}/2022-08-01"  # TODO
    response = await request(url)

    if len(response["Days"]) > 0:
        for day in response["Days"]:
            await add_group_timetable_to_db(day["DayStudyEvents"], group_id)
