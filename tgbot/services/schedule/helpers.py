""" Auxiliary functions for getting a schedule """
from datetime import date, timedelta

from aiogram.utils.i18n import get_i18n
from babel.dates import format_date


async def get_schedule_weekday_header(day: date, general_location: str = None) -> str:
    """

    :param day:
    :param general_location:
    :return:
    """
    try:
        locale = get_i18n().current_locale
    except LookupError:
        locale = 'ru'
    formatted_date = format_date(day, "EEEE, d MMMM", locale=locale)
    weekday_sticker = _get_weekday_sticker(formatted_date)
    header = f"{weekday_sticker} <b>{formatted_date}</b>\n"
    if general_location:
        header += f"📍 {general_location}\n"
    return header


def get_monday_and_sunday_dates(day_counter: int = None, week_counter: int = None) -> tuple[date, date]:
    """

    :param day_counter:
    :param week_counter:
    :return:
    """
    current_date = date.today() + timedelta(week_counter * 7 if week_counter is not None else day_counter)
    monday = current_date - timedelta(days=current_date.weekday())
    sunday = monday + timedelta(days=6)
    return monday, sunday


def get_time_sticker(hour: int) -> str:
    """

    :param hour:
    :return:
    """
    time_sticker = ""
    match hour:
        case 0 | 12:
            time_sticker = "🕛"
        case 1 | 13:
            time_sticker = "🕐"
        case 2 | 14:
            time_sticker = "🕑"
        case 3 | 15:
            time_sticker = "🕒"
        case 4 | 16:
            time_sticker = "🕓"
        case 5 | 17:
            time_sticker = "🕔"
        case 6 | 18:
            time_sticker = "🕕"
        case 7 | 19:
            time_sticker = "🕖"
        case 8 | 20:
            time_sticker = "🕗"
        case 9 | 21:
            time_sticker = "🕘"
        case 10 | 22:
            time_sticker = "🕙"
        case 11 | 23:
            time_sticker = "🕚"
    return time_sticker


def get_subject_format_sticker(subject_format: str) -> str:
    """

    :param subject_format:
    :return:
    """
    format_sticker = "✍🏼"
    match subject_format.split(" ")[0]:
        case "лекция":
            format_sticker = "🗣"
        case "практическое":
            format_sticker = "🧑🏻‍💻"
        case "лабораторная":
            format_sticker = "🔬"
        case "семинар":
            format_sticker = "💬"
        case "консультация":
            format_sticker = "🤝🏼"
        case "экзамен":
            format_sticker = "❗"
        case "зачёт":
            format_sticker = "⚠️"
    return format_sticker


def _get_weekday_sticker(day: str) -> str:
    """

    :param day:
    :return:
    """
    weekday_sticker = ""
    match day.split(",")[0]:
        case "понедельник" | "Monday":
            weekday_sticker = "1️⃣"
        case "вторник" | "Tuesday":
            weekday_sticker = "2️⃣"
        case "среда" | "Wednesday":
            weekday_sticker = "3️⃣"
        case "четверг" | "Thursday":
            weekday_sticker = "4️⃣"
        case "пятница" | "Friday":
            weekday_sticker = "5️⃣"
        case "суббота" | "Saturday":
            weekday_sticker = "6️⃣"
        case "воскресенье" | "Sunday":
            weekday_sticker = "7️⃣"
    return weekday_sticker
