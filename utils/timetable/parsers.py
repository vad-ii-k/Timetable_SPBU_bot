from datetime import date

from utils.timetable.helpers import get_weekday_sticker

TT_URL = "https://timetable.spbu.ru"


async def timetable_day_header(day_string: str) -> str:
    header = f"\n\n{await get_weekday_sticker(day_string)} <b>{day_string}</b>\n"
    return header


async def get_subject(subject_data: str, is_cancelled: bool) -> str:
    subject_name = subject_data.rsplit(sep=", ", maxsplit=1)[0]
    if is_cancelled:
        subject_name = f"<s>{subject_name}</s>"
    return subject_name


async def group_timetable_day_header(
        group_id: int, current_date: date, group_name: str
) -> str:
    header = (
        f"<b>👨‍👩‍👧‍👦 Группа: {group_name}</b>\n"
        f"📆 <a href='{TT_URL}/MATH/StudentGroupEvents/Primary/{group_id}/{current_date}'>"
        f"День: {current_date:%d.%m}</a>\n"
    )
    return header


async def group_timetable_week_header(
        group_id: int, monday: date, sunday: date, group_name: str
) -> str:
    header = (
        f"<b>👨‍👩‍👧‍👦 Группа: {group_name}</b>\n"
        f"📆 <a href='{TT_URL}/MATH/StudentGroupEvents/Primary/{group_id}/{monday}'>"
        f"Неделя: {monday:%d.%m} — {sunday:%d.%m}</a>\n"
    )
    return header


async def teacher_timetable_day_header(
        teacher_id: int, current_date: date, teacher_surname: str
) -> str:
    header = (
        f"🧑‍🏫 Преподаватель: <b>{teacher_surname}</b>\n"
        f"📆 <a href='{TT_URL}/WeekEducatorEvents/{teacher_id}/{current_date}'>"
        f"День: {current_date:%d.%m}</a> \n"
    )
    return header


async def teacher_timetable_week_header(
        teacher_id: int, monday: date, sunday: date, teacher_surname: str
) -> str:
    header = (
        f"🧑‍🏫 Преподаватель: <b>{teacher_surname}</b>\n"
        f"📆 <a href='{TT_URL}/WeekEducatorEvents/{teacher_id}/{monday}'>"
        f"Неделя: {monday:%d.%m} — {sunday:%d.%m}</a>\n"
    )
    return header
