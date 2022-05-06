import pytz

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.util import astimezone

from tgbot.config import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD
from tgbot.loader import db
from utils.timetable.api import fill_group_timetable_from_tt

redis_job_storage = RedisJobStore(db=1, host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD)
redis_job_storage.remove_all_jobs()
scheduler = AsyncIOScheduler(jobstores={'redis': redis_job_storage},
                             timezone=astimezone(pytz.timezone('Europe/Moscow')))


@scheduler.scheduled_job('cron', hour="6-22", jobstore='redis')
async def groups_timetable_updating():
    active_groups_tt_ids = await db.get_active_groups_tt_ids()
    for group_tt_id in active_groups_tt_ids:
        await fill_group_timetable_from_tt(group_tt_id)


async def start_scheduler():
    scheduler.start()
