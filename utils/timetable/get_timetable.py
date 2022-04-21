from datetime import date

import loader
from utils.db_api.db_timetable import get_group_timetable_week_from_db, get_group_timetable_day_from_db
from utils.image_converter.new_converter import TimetableIMG
from utils.timetable.api import fill_group_timetable_from_tt
from utils.timetable.helpers import calculator_of_week_days, calculator_of_days
from utils.timetable.parsers import group_timetable_day_header, group_timetable_week_header, timetable_day_header


async def get_group_timetable(tt_id: id, week_counter: int = None, day_counter: int = None):
    group_db = await loader.db.get_group_by_tt_id(tt_id)
    if not group_db.is_received_schedule:
        await fill_group_timetable_from_tt(tt_id)
        await group_db.update(is_received_schedule=not group_db.is_received_schedule).apply()

    if week_counter is not None:
        monday, sunday = await calculator_of_week_days(week_counter)
        timetable_db = await get_group_timetable_week_from_db(group_db.group_id, monday, sunday)
        timetable_text = await get_text_group_timetable_week(tt_id, group_db.name, monday, sunday, timetable_db)
    else:
        current_date, next_day = await calculator_of_days(day_counter)
        timetable_db = await get_group_timetable_day_from_db(group_db.group_id, current_date)
        timetable_text = await get_text_group_timetable_day(tt_id, group_db.name, current_date, timetable_db)
    return timetable_text


async def get_text_group_timetable_day(group_id: int, group_name: str, current_date: date, timetable_db) -> str:
    timetable = await group_timetable_day_header(group_id, current_date, group_name)

    schedule_pic = TimetableIMG("utils/image_converter/output.png")
    schedule_pic.image_title(title=group_name, date=current_date.strftime("%A, %d %B"))

    if len(timetable_db[0].events) > 0:
        timetable += await group_timetable_parser_day(timetable_db[0].date, timetable_db[0].events)
        schedule_pic.insert_timetable(timetable_db[0].date.strftime('%A, %d %B'), timetable_db[0].events)
    else:
        timetable += '\n🏖 <i>Занятий в этот день нет</i>'
    schedule_pic.crop_image()
    return timetable


async def get_text_group_timetable_week(group_id: int, group_name: str, monday: date, sunday: date, timetable_db) -> str:
    timetable = await group_timetable_week_header(group_id, monday, sunday, group_name)

    schedule_pic = TimetableIMG("utils/image_converter/output.png")
    schedule_pic.image_title(title=group_name, date="Неделя: {monday} — {sunday}".format(
                                                    monday=monday.strftime("%d.%m"), sunday=sunday.strftime("%d.%m")))

    if len(timetable_db) > 0:
        for day in timetable_db:
            day_timetable = await group_timetable_parser_day(day.date, day.events)
            schedule_pic.insert_timetable(day.date.strftime('%A, %d %B'), day.events)
            if len(timetable) + len(day_timetable) < 4000:
                timetable += day_timetable
            else:
                timetable += "\n\nСообщение слишком длинное..."
                break
    else:
        timetable += '\n🏖 <i>Занятий на этой неделе нет</i>'
    schedule_pic.crop_image()
    return timetable


async def group_timetable_parser_day(day: date, events: list):
    day_timetable = await timetable_day_header(day.strftime('%A, %d %B'))
    for event in events:
        day_timetable += "  ┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈\n" \
                     f"   <b>{event.subject_name}</b>\n" \
                     f"    🕟 <u>{event.start_time.strftime('%H:%M')}-{event.end_time.strftime('%H:%M')}</u>\n" \
                     f"    🧑‍🏫 Преподаватель: <i>{event.educator}</i>\n" \
                     f"    ✍🏻 Формат: <i>{event.subject_format}</i>\n" \
                     f"    🚩 Место: <i>{event.locations}</i>\n"
    return day_timetable