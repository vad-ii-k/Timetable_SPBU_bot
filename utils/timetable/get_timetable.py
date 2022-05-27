from datetime import date
from typing import List

from babel.dates import format_date

from tgbot import loader
from utils.db_api.db_timetable import StudyEvent, TimetableOneDay, get_timetable_day_from_db
from utils.db_api.db_timetable import get_timetable_week_from_db
from utils.image_converter.converter import TimetableIMG
from utils.timetable.api import fill_timetable_from_tt
from utils.timetable.helpers import (
    calculator_of_week_days,
    calculator_of_days,
    is_basic_events_info_identical,
)
from utils.timetable.parsers import (
    teacher_timetable_day_header,
    teacher_timetable_week_header,
    timetable_day_header,
    group_timetable_week_header,
    group_timetable_day_header,
)


async def get_timetable(
    tt_id: int, is_picture: bool, user_type: str, week_counter: int = None, day_counter: int = None
) -> str:
    if user_type == "student":
        group_db = await loader.db.get_group_by_tt_id(tt_id)
        if not group_db.is_received_schedule:
            await fill_timetable_from_tt(tt_id, user_type)
            await group_db.update(is_received_schedule=not group_db.is_received_schedule).apply()
        db_id: int = group_db.group_id
        tt_name: str = group_db.name
    else:
        teacher_spbu_db = await loader.db.get_teacher_spbu_by_tt_id(tt_id)
        if teacher_spbu_db is None or teacher_spbu_db.full_name is None:
            # The second condition is a patch due to a bug, you can remove it
            await fill_timetable_from_tt(tt_id, user_type)
            teacher_spbu_db = await loader.db.get_teacher_spbu_by_tt_id(tt_id)
        db_id: int = teacher_spbu_db.teacher_spbu_id
        tt_name: str = teacher_spbu_db.full_name

    if week_counter is not None:
        monday, sunday = await calculator_of_week_days(week_counter)
        timetable_db = await get_timetable_week_from_db(db_id, monday, sunday, user_type)
        if is_picture:
            timetable_text = await get_image_timetable_week(
                tt_id, tt_name, monday, sunday, timetable_db, user_type
            )
        else:
            timetable_text = await get_text_timetable_week(
                tt_id, tt_name, monday, sunday, timetable_db, user_type
            )
    else:
        current_date = (await calculator_of_days(day_counter))[0]
        timetable_db = await get_timetable_day_from_db(db_id, current_date, user_type)
        if is_picture:
            timetable_text = await get_image_timetable_day(
                tt_id, tt_name, current_date, timetable_db, user_type
            )
        else:
            timetable_text = await get_text_timetable_day(
                tt_id, tt_name, current_date, timetable_db, user_type
            )
    return timetable_text


async def get_text_timetable_day(
        tt_id: int,
        tt_name: str,
        current_date: date,
        timetable_db: List[TimetableOneDay],
        user_type: str,
) -> str:
    timetable = ""
    if user_type == "teacher":
        timetable = await teacher_timetable_day_header(tt_id, current_date, tt_name)
    elif user_type == "student":
        timetable = await group_timetable_day_header(tt_id, current_date, tt_name)

    if len(timetable_db[0].events) > 0:
        day_timetable = await timetable_parser_day(
            day=timetable_db[0].date, events=timetable_db[0].events, user_type="teacher"
        )
        if len(timetable) + len(day_timetable) < 4096:
            timetable += day_timetable
        else:
            timetable += "\n\n📛 Сообщение слишком длинное..."
    else:
        timetable += "\n🏖 <i>Занятий в этот день нет</i>"
    return timetable


async def get_image_timetable_day(
        tt_id: int,
        tt_name: str,
        current_date: date,
        timetable_db: List[TimetableOneDay],
        user_type: str,
) -> str:
    timetable = ""
    if user_type == "teacher":
        timetable = await teacher_timetable_day_header(tt_id, current_date, tt_name)
    elif user_type == "student":
        timetable = await group_timetable_day_header(tt_id, current_date, tt_name)

    schedule_pic = TimetableIMG("utils/image_converter/output.png")
    schedule_pic.create_image_title(
        title=tt_name, date=format_date(current_date, "EEEE, d MMMM", locale="ru_RU")
    )

    if len(timetable_db[0].events) > 0:
        schedule_pic.insert_timetable(
            date=format_date(timetable_db[0].date, "EEEE, d MMMM", locale="ru_RU"),
            events=timetable_db[0].events,
        )
    schedule_pic.crop_image()
    return timetable


async def get_text_timetable_week(
        tt_id: int,
        tt_name: str,
        monday: date,
        sunday: date,
        timetable_db: List[TimetableOneDay],
        user_type: str,
) -> str:
    timetable = ""
    if user_type == "teacher":
        timetable = await teacher_timetable_week_header(tt_id, monday, sunday, tt_name)
    elif user_type == "student":
        timetable = await group_timetable_week_header(tt_id, monday, sunday, tt_name)

    if len(timetable_db) > 0:
        for day in timetable_db:
            day_timetable = await timetable_parser_day(
                day=day.date, events=day.events, user_type="teacher"
            )
            if len(timetable) + len(day_timetable) < 4060:
                timetable += day_timetable
            else:
                timetable += "\n\n📛 Сообщение слишком длинное..."
                break
    else:
        timetable += "\n🏖 <i>Занятий на этой неделе нет</i>"
    return timetable


async def get_image_timetable_week(
        tt_id: int,
        tt_name: str,
        monday: date,
        sunday: date,
        timetable_db: List[TimetableOneDay],
        user_type: str,
) -> str:
    timetable = ""
    if user_type == "teacher":
        timetable = await teacher_timetable_week_header(tt_id, monday, sunday, tt_name)
    elif user_type == "student":
        timetable = await group_timetable_week_header(tt_id, monday, sunday, tt_name)

    schedule_pic = TimetableIMG("utils/image_converter/output.png")
    schedule_pic.create_image_title(
        title=tt_name,
        date=f"Неделя: {monday:%d.%m} — {sunday:%d.%m}",
    )
    if len(timetable_db) > 0:
        for day in timetable_db:
            schedule_pic.insert_timetable(
                date=format_date(day.date, "EEEE, d MMMM", locale="ru_RU"),
                events=day.events,
            )
    schedule_pic.crop_image()
    return timetable


async def timetable_parser_day(day: date, events: List[StudyEvent], user_type: str) -> str:
    day_timetable = await timetable_day_header(format_date(day, "EEEE, d MMMM", locale="ru_RU"))
    for i, event in enumerate(events):
        if i == 0 or is_basic_events_info_identical(events[i - 1], events[i]):
            day_timetable += (
                '   ┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈\n'
                f'   {"<s>" if event.is_canceled else ""}'
                f'<b>{event.subject_name}</b>'
                f'{"</s>" if event.is_canceled else ""}\n'
                f'    🕟 <u>{event.start_time:%H:%M}-{event.end_time:%H:%M}</u>\n'
                f'    ✍🏻 Формат: <i>{event.subject_format}</i>\n'
            )
        day_timetable += (
            f"    ╔ {'🧑‍🏫' if user_type == 'student' else '🎓'}"
            f" <i>{event.contingent}</i>\n"
            f"    ╚ 🚩 <i>{event.locations}</i>\n"
        )
    return day_timetable
