import pytz
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.util import astimezone

from tgbot import config
from tgbot.config import REDIS_HOST, REDIS_PASSWORD, REDIS_PORT
from utils.db_api.db_commands import DBCommands

bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)

storage = RedisStorage2(
    host=REDIS_HOST, port=REDIS_PORT, db=0, password=REDIS_PASSWORD
)
dp = Dispatcher(bot, storage=storage)
db = DBCommands()

redis_job_storage = RedisJobStore(
    host=REDIS_HOST, port=REDIS_PORT, db=1, password=REDIS_PASSWORD
)
redis_job_storage.remove_all_jobs()
scheduler = AsyncIOScheduler(
    jobstores={"redis": redis_job_storage},
    timezone=astimezone(pytz.timezone("Europe/Moscow")),
)
