async def teacher_timetable_parser(info):
    timetable = "<b>Преподаватель</b>  {}\n".format(info.get("EducatorDisplayText"))
    timetable += "<a href='{}'>Текущая неделя</a> \n".format(
        f"https://timetable.spbu.ru/WeekEducatorEvents/{info['EducatorMasterId']}")
    if len(info["EducatorEventsDays"]) > 0:
        for day in info["EducatorEventsDays"]:
            timetable += "\n<b>{}</b>\n".format(day.get("DayString"))
            events = day["DayStudyEvents"]
            for event in events:
                timetable += "  <u>{}</u>\n".format(event.get("TimeIntervalString"))
                (subject, lesson_format) = event.get("Subject").split(", ")
                timetable += "  <b>{}</b>\n    <i>{}</i>\n".format(subject, lesson_format)
                timetable += "    {}\n".format(event.get("ContingentUnitName"))
                timetable += "    <i>{}</i>\n".format(event.get("LocationsDisplayText"))
    return timetable
