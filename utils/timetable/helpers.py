from datetime import timedelta, date


async def calculator_of_days(day_counter: int) -> tuple:
    if day_counter > 0:
        current_date = date.today() + timedelta(day_counter)
    else:
        current_date = date.today() - timedelta(-day_counter)
    next_day = current_date + timedelta(days=1)
    return current_date, next_day


async def calculator_of_week_days(week_counter: int) -> tuple:
    current_date = date.today() + timedelta(week_counter * 7)
    monday = current_date - timedelta(days=current_date.weekday())
    sunday = monday + timedelta(days=6)
    return monday, sunday


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
