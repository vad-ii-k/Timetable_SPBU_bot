from tgbot.loader import db, scheduler
from utils.timetable.api import fill_timetable_from_tt


@scheduler.scheduled_job("cron", hour="1, 13", jobstore="redis")
async def job_timetable_updating() -> None:
    active_groups_tt_ids = await db.get_active_groups_tt_ids()
    for group_tt_id in active_groups_tt_ids:
        await fill_timetable_from_tt(group_tt_id, "student")
    active_teachers_tt_ids = await db.get_active_teachers_tt_ids()
    for teacher_tt_id in active_teachers_tt_ids:
        await fill_timetable_from_tt(teacher_tt_id, "teacher")


@scheduler.scheduled_job("cron", hour="4", jobstore="redis")
async def job_clearing_db_unused_info() -> None:
    await db.clearing_unused_info()


async def start_scheduler() -> None:
    scheduler.start()
