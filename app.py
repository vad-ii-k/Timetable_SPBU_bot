import asyncio
import sys

from aiogram import executor

from tgbot.notify_admins import on_startup_notify
from tgbot.loader import dp
from tgbot.set_bot_commands import set_default_commands
from utils.db_api.db_commands import create_db
from utils.db_api.initial_filling_of_db import adding_groups_to_db
from utils.db_api.updating_of_db import start_scheduler


async def on_startup(dispatcher) -> None:
    await create_db()
    await adding_groups_to_db()
    await start_scheduler()
    await set_default_commands(dispatcher)
    await on_startup_notify(dispatcher)


async def on_shutdown(dispatcher) -> None:
    await dp.storage.close()
    await dp.storage.wait_closed()


if __name__ == '__main__':
    if sys.version_info[0] == 3 and sys.version_info[1] >= 8 and sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)
