async def separating_long_str(string: str) -> str:
    if len(string) > 45:
        sep = string.find(' ', len(string) // 2 - 6, len(string) // 2 + 7)
        if sep != -1:
            first_part = string[0:sep]
            second_part = string[sep + 1:len(string)]
            string = first_part + '\n  ' + second_part
    return string


async def teacher_timetable_parser_day(day: dict) -> str:
    timetable = "\n<b>{data}</b>\n".format(data=day.get("DayString"))
    events = day["DayStudyEvents"]
    for event in events:
        time = event.get("TimeIntervalString")
        subject = await separating_long_str(event.get("Subject").split(", ")[0])
        lesson_format = event.get("Subject").split(", ")[1]
        contingent = await separating_long_str(event.get("ContingentUnitName"))
        locations = "Онлайн" if event.get("LocationsDisplayText").find("С использованием инф") != -1\
            else event.get("LocationsDisplayText")

        timetable += f"  <u>{time}</u>\n" \
                     f"  <b>{subject}</b>\n" \
                     f"    Формат: <i>{lesson_format}</i>\n" \
                     f"    Группы: <b>{contingent}</b>\n" \
                     f"    Место: <i>{locations}</i>\n"
    return timetable
