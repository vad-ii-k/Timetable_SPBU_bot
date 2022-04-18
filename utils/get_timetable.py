import loader
from utils.timetable.api import fill_group_timetable_from_tt
from utils.timetable.helpers import calculator_of_week_days, calculator_of_days


async def get_group_timetable(tt_id: id, week_counter: int = None, day_counter: int = None):
    group_db = await loader.db.get_group_by_tt_id(tt_id)
    if not group_db.is_received_schedule:
        await fill_group_timetable_from_tt(tt_id)

    if week_counter is not None:
        monday, sunday = await calculator_of_week_days(week_counter)
        timetable_db = await loader.db.get_group_timetable_week(group_db.group_id, monday, sunday)
    else:
        current_date, next_day = await calculator_of_days(day_counter)
        timetable_db = await loader.db.get_group_timetable_day(group_db.group_id, current_date)
    print(timetable_db)
