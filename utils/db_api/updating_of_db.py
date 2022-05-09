from tgbot.loader import db, scheduler
from utils.timetable.api import fill_group_timetable_from_tt, fill_teacher_timetable_from_tt


@scheduler.scheduled_job('cron', hour="1, 13", jobstore='redis')
async def job_timetable_updating() -> None:
    active_groups_tt_ids = await db.get_active_groups_tt_ids()
    for group_tt_id in active_groups_tt_ids:
        await fill_group_timetable_from_tt(group_tt_id)
    active_teachers_tt_ids = await db.get_active_teachers_tt_ids()
    for teacher_tt_id in active_teachers_tt_ids:
        await fill_teacher_timetable_from_tt(teacher_tt_id)


async def start_scheduler() -> None:
    scheduler.start()
