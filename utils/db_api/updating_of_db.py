from tgbot.loader import db, scheduler
from tgbot.notifications import job_send_daily_summary
from utils.timetable.api import fill_timetable_from_tt


async def job_timetable_updating() -> None:
    active_groups_tt_ids = await db.get_active_groups_tt_ids()
    for group_tt_id in active_groups_tt_ids:
        await fill_timetable_from_tt(group_tt_id, "student")
    active_teachers_tt_ids = await db.get_active_teachers_tt_ids()
    for teacher_tt_id in active_teachers_tt_ids:
        await fill_timetable_from_tt(teacher_tt_id, "teacher")


async def start_scheduler() -> None:
    scheduler.add_job(db.clearing_unused_info, "cron", hour="4", jobstore="redis")
    scheduler.add_job(job_timetable_updating, "cron", hour="1, 13", jobstore="redis")
    scheduler.add_job(job_send_daily_summary, "cron", hour="7-9, 19-21", jobstore="redis")
    scheduler.start()
