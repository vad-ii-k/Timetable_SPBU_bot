from datetime import date, timedelta


def _get_monday_and_sunday_dates(week_counter: int = 0) -> tuple[date, date]:
    current_date = date.today() + timedelta(week_counter * 7)
    monday = current_date - timedelta(days=current_date.weekday())
    sunday = monday + timedelta(days=6)
    return monday, sunday


def _get_schedule_weekday_header(day_string: str) -> str:
    weekday_sticker = _get_weekday_sticker(day_string)
    header = f"\n\n{weekday_sticker} <b>{day_string}</b>\n"
    return header


def _get_time_sticker(hour: int) -> str:
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


def _get_subject_format_sticker(subject_format: str) -> str:
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
