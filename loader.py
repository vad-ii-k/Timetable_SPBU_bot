from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.redis import RedisStorage2

from data import config
from utils.db_api.db_commands import DBCommands

bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = RedisStorage2(host="localhost", port=6379, db=0, password="redis")

dp = Dispatcher(bot, storage=storage)
db = DBCommands()
