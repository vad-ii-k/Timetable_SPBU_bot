async def separating_long_str(string: str) -> str:
    if len(string) > 90:
        sep1 = string.find(' ', len(string) // 3 - 6, len(string) // 3 + 7)
        sep2 = string.find(' ', 2 * len(string) // 3 - 6, 2 * len(string) // 3 + 7)
        if sep1 != -1 and sep2 != -1:
            first_part = string[0:sep1]
            second_part = string[sep1 + 1:sep2]
            third_part = string[sep2 + 1:len(string)]
            string = first_part + '\n  ' + second_part + '\n  ' + third_part
    elif len(string) > 45:
        sep = string.find(' ', len(string) // 2 - 6, len(string) // 2 + 7)
        if sep != -1:
            first_part = string[0:sep]
            second_part = string[sep + 1:len(string)]
            string = first_part + '\n  ' + second_part
    return string


async def get_weekday_sticker(day: str):
    weekday_sticker = ''
    match day.split(",")[0]:
        case 'понедельник':
            weekday_sticker = '1️⃣'
        case 'вторник':
            weekday_sticker = '2️⃣'
        case 'среда':
            weekday_sticker = '3️⃣'
        case 'четверг':
            weekday_sticker = '4️⃣'
        case 'пятница':
            weekday_sticker = '5️⃣'
        case 'суббота':
            weekday_sticker = '6️⃣'
        case 'воскресенье':
            weekday_sticker = '7️⃣'
    return weekday_sticker


async def teacher_timetable_parser_day(day: dict) -> str:
    timetable = "\n\n{sticker} <b>{data}</b>\n".format(sticker=await get_weekday_sticker(day.get("DayString")),
                                                       data=day.get("DayString"))
    events = day["DayStudyEvents"]
    for event in events:
        time = event.get("TimeIntervalString")
        subject = await separating_long_str(event.get("Subject").split(", ")[0])
        if event.get("IsCancelled"):
            subject = f"<s>{subject}</s>"
        lesson_format = event.get("Subject").split(", ")[1]
        contingent = await separating_long_str(event.get("ContingentUnitName"))
        locations = "Онлайн" if event.get("LocationsDisplayText").find("С использованием инф") != -1\
            else await separating_long_str(event.get("LocationsDisplayText"))

        timetable += "  ┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈\n"\
                     f"     <b>{subject}</b>\n" \
                     f"    🕟 <u>{time}</u>\n" \
                     f"    🎓 Группы: <b>{contingent}</b>\n" \
                     f"    ✍🏻 Формат: <i>{lesson_format}</i>\n" \
                     f"    🚩 Место: <i>{locations}</i>\n" \

    return timetable
