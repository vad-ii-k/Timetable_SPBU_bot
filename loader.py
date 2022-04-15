from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from data import config
from utils.db_api.db_commands import DBCommands

bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()

# TODO
'''
from aiogram.contrib.fsm_storage.redis import RedisStorage2

storage = RedisStorage2(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    password=REDIS_PASSWORD
)
'''

dp = Dispatcher(bot, storage=storage)
db = DBCommands()
