async def teacher_timetable_parser_day(day) -> str:
    timetable = "\n<b>{data}</b>\n".format(data=day.get("DayString"))
    events = day["DayStudyEvents"]
    for event in events:
        timetable += "  <u>{time}</u>\n" \
                     "  <b>{subject}</b>\n" \
                     "    <i>{lesson_format}</i>\n" \
                     "    {contingent}\n" \
                     "    <i>{locations}</i>\n".format(
                            time=event.get("TimeIntervalString"),
                            subject=event.get("Subject").split(", ")[0],
                            lesson_format=event.get("Subject").split(", ")[1],
                            contingent=event.get("ContingentUnitName"),
                            locations=event.get("LocationsDisplayText")
                        )
    return timetable
