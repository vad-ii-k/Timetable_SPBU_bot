from datetime import date

from utils.timetable.helpers import separating_long_str, get_weekday_sticker


async def timetable_day_header(day_string: str) -> str:
    header = "\n\n{sticker} <b>{data}</b>\n".format(sticker=await get_weekday_sticker(day_string),
                                                    data=day_string)
    return header


async def get_subject(subject_data: str, is_cancelled: bool) -> str:
    subject_name = await separating_long_str(subject_data.rsplit(sep=", ", maxsplit=1)[0])
    if is_cancelled:
        subject_name = f"<s>{subject_name}</s>"
    return subject_name


async def get_locations(locations_data: str) -> str:
    locations = "Онлайн" if locations_data.find("С использованием инф") != -1\
            else await separating_long_str(locations_data)
    return locations


async def teacher_timetable_parser_day(day: dict) -> str:
    timetable = await timetable_day_header(day.get("DayString"))
    events = day["DayStudyEvents"]
    for event in events:
        time = event.get("TimeIntervalString")
        subject = await get_subject(subject_data=event.get("Subject"), is_cancelled=event.get("IsCancelled"))
        lesson_format = event.get("Subject").rsplit(sep=", ", maxsplit=1)[1]
        contingent = await separating_long_str(event.get("ContingentUnitName"))
        locations = await get_locations(locations_data=event.get("LocationsDisplayText"))

        timetable += "  ┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈\n" \
                     f"     <b>{subject}</b>\n" \
                     f"    🕟 <u>{time}</u>\n" \
                     f"    🎓 Группы: <b>{contingent}</b>\n" \
                     f"    ✍🏻 Формат: <i>{lesson_format}</i>\n" \
                     f"    🚩 Место: <i>{locations}</i>\n"
    return timetable


async def group_timetable_day_header(group_id: int, current_date: date, group_name: str) -> str:
    header = "<b>👨‍👩‍👧‍👦 Группа {group_name}</b>\n📆 <a href='{link}'>День: {current_date}</a>\n".format(
        group_name=group_name,
        link=f"https://timetable.spbu.ru/MATH/StudentGroupEvents/Primary/{group_id}/{current_date}",
        current_date=current_date.strftime("%d.%m")
    )
    return header


async def group_timetable_week_header(group_id: int, monday: date, sunday: date, group_name: str) -> str:
    header = "<b>👨‍👩‍👧‍👦 Группа {group_name}</b>\n📆 <a href='{link}'>Неделя: {monday} — {sunday}</a>\n".format(
        group_name=group_name,
        link=f"https://timetable.spbu.ru/MATH/StudentGroupEvents/Primary/{group_id}/{monday}",
        monday=monday.strftime("%d.%m"),
        sunday=sunday.strftime("%d.%m")
    )
    return header


async def teacher_timetable_day_header(teacher_id: int, current_date: date, response: dict) -> str:
    header = "Преподаватель: <b>{educator}</b>\n📆 <a href='{link}'>День: {current_date}</a> \n".format(
        educator=response.get("EducatorDisplayText"),
        link=f"https://timetable.spbu.ru/WeekEducatorEvents/{teacher_id}/{current_date}",
        current_date=current_date.strftime("%d.%m")
    )
    return header


async def teacher_timetable_week_header(teacher_id: int, monday: date, sunday: date, response: dict) -> str:
    header = "Преподаватель: <b>{educator}</b>\n📆 <a href='{link}'>Неделя: {monday} — {sunday}</a>\n".format(
        educator=response.get("EducatorDisplayText"),
        link=f"https://timetable.spbu.ru/WeekEducatorEvents/{teacher_id}/{monday}",
        monday=monday.strftime("%d.%m"),
        sunday=sunday.strftime("%d.%m")
    )
    return header
