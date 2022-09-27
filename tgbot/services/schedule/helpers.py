from datetime import date, timedelta


async def _get_monday_and_sunday_dates(week_counter: int = 0) -> tuple[date, date]:
    current_date = date.today() + timedelta(week_counter * 7)
    monday = current_date - timedelta(days=current_date.weekday())
    sunday = monday + timedelta(days=6)
    return monday, sunday
