import asyncio
import sys

from aiogram import executor
from loader import dp
import middlewares, filters, handlers
from utils.db_api.db_commands import create_db
from utils.db_api.initial_filling_of_db import adding_groups_to_db
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands


async def on_startup(dispatcher):
    # Setting default commands
    await set_default_commands(dispatcher)

    # Creating a new DB
    await create_db()

    # Launch Notification
    # await on_startup_notify(dispatcher)

    if sys.version_info[0] == 3 and sys.version_info[1] >= 8 and sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    await adding_groups_to_db()


async def on_shutdown(dispatcher):
    await dp.storage.close()
    await dp.storage.wait_closed()


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)
