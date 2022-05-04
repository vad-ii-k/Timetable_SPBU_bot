from datetime import date
from babel.dates import format_date

from tgbot import loader
from utils.db_api.db_teacher_timetable import get_teacher_timetable_week_from_db, get_teacher_timetable_day_from_db, TeacherEvent
from utils.image_converter.converter import TimetableIMG
from utils.timetable.api import fill_teacher_timetable_from_tt
from utils.timetable.helpers import calculator_of_week_days, calculator_of_days
from utils.timetable.parsers import teacher_timetable_day_header, teacher_timetable_week_header, timetable_day_header


async def get_teacher_timetable(tt_id: id, is_picture: bool, week_counter: int = None, day_counter: int = None):
    teacher_spbu_db = await loader.db.get_teacher_spbu_by_tt_id(tt_id)
    if teacher_spbu_db is None:
        await fill_teacher_timetable_from_tt(tt_id)
        teacher_spbu_db = await loader.db.get_teacher_spbu_by_tt_id(tt_id)

    if week_counter is not None:
        monday, sunday = await calculator_of_week_days(week_counter)
        timetable_db = await get_teacher_timetable_week_from_db(teacher_spbu_db.teacher_spbu_id, monday, sunday)
        if is_picture:
            timetable_text = await get_image_teacher_timetable_week(tt_id, teacher_spbu_db.full_name, monday, sunday, timetable_db)
        else:
            timetable_text = await get_text_teacher_timetable_week(tt_id, teacher_spbu_db.full_name, monday, sunday, timetable_db)
    else:
        current_date, next_day = await calculator_of_days(day_counter)
        timetable_db = await get_teacher_timetable_day_from_db(teacher_spbu_db.teacher_spbu_id, current_date)
        if is_picture:
            timetable_text = await get_image_teacher_timetable_day(tt_id, teacher_spbu_db.full_name, current_date, timetable_db)
        else:
            timetable_text = await get_text_teacher_timetable_day(tt_id, teacher_spbu_db.full_name, current_date, timetable_db)
    return timetable_text


async def get_text_teacher_timetable_day(teacher_id: int, teacher_name: str, current_date: date, timetable_db) -> str:
    timetable = await teacher_timetable_day_header(teacher_id, current_date, teacher_name)

    if len(timetable_db[0].events) > 0:
        day_timetable = await teacher_timetable_parser_day(day=timetable_db[0].date, events=timetable_db[0].events)
        if len(timetable) + len(day_timetable) < 4096:
            timetable += day_timetable
        else:
            timetable += "\n\n📛 Сообщение слишком длинное..."
    else:
        timetable += '\n🏖 <i>Занятий в этот день нет</i>'
    return timetable


async def get_image_teacher_timetable_day(group_id: int, group_name: str, current_date: date, timetable_db) -> str:
    timetable = await teacher_timetable_day_header(group_id, current_date, group_name)

    schedule_pic = TimetableIMG("utils/image_converter/output.png")
    schedule_pic.create_image_title(title=group_name, date=format_date(current_date, 'EEEE, d MMMM', locale='ru_RU'))

    if len(timetable_db[0].events) > 0:
        schedule_pic.insert_timetable(date=format_date(timetable_db[0].date, 'EEEE, d MMMM', locale='ru_RU'),
                                      events=timetable_db[0].events)
    schedule_pic.crop_image()
    return timetable


async def get_text_teacher_timetable_week(teacher_id: int, teacher_name: str, monday: date, sunday: date,
                                          timetable_db) -> str:
    timetable = await teacher_timetable_week_header(teacher_id, monday, sunday, teacher_name)

    if len(timetable_db) > 0:
        for day in timetable_db:
            day_timetable = await teacher_timetable_parser_day(day=day.date, events=day.events)
            if len(timetable) + len(day_timetable) < 4096:
                timetable += day_timetable
            else:
                timetable += "\n\n📛 Сообщение слишком длинное..."
                break
    else:
        timetable += '\n🏖 <i>Занятий на этой неделе нет</i>'
    return timetable


async def get_image_teacher_timetable_week(group_id: int, group_name: str, monday: date, sunday: date, timetable_db) -> str:
    timetable = await teacher_timetable_week_header(group_id, monday, sunday, group_name)

    schedule_pic = TimetableIMG("utils/image_converter/output.png")
    schedule_pic.create_image_title(title=group_name, date="Неделя: {monday} — {sunday}".format(
        monday=monday.strftime("%d.%m"), sunday=sunday.strftime("%d.%m")))
    if len(timetable_db) > 0:
        for day in timetable_db:
            schedule_pic.insert_timetable(date=format_date(day.date, 'EEEE, d MMMM', locale='ru_RU'),
                                          events=day.events)
    schedule_pic.crop_image()
    return timetable


async def teacher_timetable_parser_day(day: date, events: list[TeacherEvent]):
    day_timetable = await timetable_day_header(format_date(day, 'EEEE, d MMMM', locale='ru_RU'))
    for event in events:
        day_timetable += "   ┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈\n"
        day_timetable += f"   <s><b>{event.subject_name}</b></s>\n" if event.is_canceled \
            else f"   <b>{event.subject_name}</b>\n"
        day_timetable += f"    🕟 <u>{event.start_time.strftime('%H:%M')}-{event.end_time.strftime('%H:%M')}</u>\n" \
                         f"    🎓 Группы: <i>{event.groups}</i>\n" \
                         f"    ✍🏻 Формат: <i>{event.subject_format}</i>\n" \
                         f"    🚩 Место: <i>{event.locations}</i>\n"
    return day_timetable
