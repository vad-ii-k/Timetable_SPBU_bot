from datetime import date

from utils.timetable.helpers import separating_long_str, get_weekday_sticker


async def timetable_day_header(day_string: str) -> str:
    header = "\n\n{sticker} <b>{data}</b>\n".format(sticker=await get_weekday_sticker(day_string),
                                                    data=day_string)
    return header


async def get_subject(subject_data: str, is_cancelled: bool) -> str:
    subject_name = await separating_long_str(subject_data.split(", ")[0])
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
        lesson_format = event.get("Subject").split(", ")[1]
        contingent = await separating_long_str(event.get("ContingentUnitName"))
        locations = await get_locations(locations_data=event.get("LocationsDisplayText"))

        timetable += "  ┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈\n" \
                     f"     <b>{subject}</b>\n" \
                     f"    🕟 <u>{time}</u>\n" \
                     f"    🎓 Группы: <b>{contingent}</b>\n" \
                     f"    ✍🏻 Формат: <i>{lesson_format}</i>\n" \
                     f"    🚩 Место: <i>{locations}</i>\n" \

    return timetable


async def add_event(old_dict: dict, new_list: list):
    time = old_dict.get("TimeIntervalString")
    subject = await get_subject(subject_data=old_dict.get("Subject"), is_cancelled=old_dict.get("IsCancelled"))
    lesson_format = old_dict.get("Subject").split(", ")[1]
    educator = await separating_long_str(old_dict.get("EducatorsDisplayText").split(',')[0])
    locations = await get_locations(locations_data=old_dict.get("LocationsDisplayText"))
    new_list.append({"time": time, "subject": subject, "lesson_format": lesson_format,
                     "educator": educator, "locations": locations})


async def group_timetable_parser_day(day: dict) -> str:
    timetable = await timetable_day_header(day.get("DayString"))
    events = day["DayStudyEvents"]
    events_set = []
    if len(day["DayStudyEvents"]) >= 1:
        await add_event(events[0], events_set)
        for i in range(1, len(events)):
            if events[i - 1]["TimeIntervalString"] == events[i]["TimeIntervalString"]\
                    and events[i - 1]["Subject"] == events[i]["Subject"]:
                events_set[len(events_set) - 1]["educator"] += ";\n  " +\
                                                               events[i].get("EducatorsDisplayText").split(',')[0]
                if events_set[len(events_set) - 1]["locations"] != events[i].get("locations")\
                        and events_set[len(events_set) - 1]["locations"] != "Онлайн":
                    events_set[len(events_set) - 1]["locations"] += ";\n  " + events[i].get("LocationsDisplayText")
            else:
                await add_event(events[i], events_set)

    for event in events_set:
        timetable += "  ┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈\n" \
                     f"   <b>{event.get('subject')}</b>\n" \
                     f"    🕟 <u>{event.get('time')}</u>\n" \
                     f"    🧑‍🏫 Преподаватель: <i>{event.get('educator')}</i>\n" \
                     f"    ✍🏻 Формат: <i>{event.get('lesson_format')}</i>\n" \
                     f"    🚩 Место: <i>{event.get('locations')}</i>\n"
    return timetable


async def group_timetable_day_header(group_id: int, current_date: date, response: dict) -> str:
    header = "<b>{group}</b>\n📆 <a href='{link}'>День: {current_date}</a>\n".format(
        group=response.get("StudentGroupDisplayName"),
        link=f"https://timetable.spbu.ru/MATH/StudentGroupEvents/Primary/{group_id}/{current_date}",
        current_date=current_date.strftime("%d.%m")
    )
    return header


async def group_timetable_week_header(group_id: int, monday: date, sunday: date, response: dict) -> str:
    header = "<b>{group}</b>\n📆 <a href='{link}'>Неделя: {monday} — {sunday}</a>\n".format(
        group=response.get("StudentGroupDisplayName"),
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
