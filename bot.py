import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from tgbot.commands import set_commands
from tgbot.config import config
from tgbot.handlers.admin import admin_router
from tgbot.handlers.commands import router as commands_router
from tgbot.handlers.search_educator import router as search_educator_router
from tgbot.handlers.search_group import router as search_group_router
from tgbot.handlers.start_menu import router as start_menu_router
from tgbot.handlers.student_navigation import router as student_navigation_router
from tgbot.middlewares.config import ConfigMessageMiddleware, ConfigCallbackMiddleware
from tgbot.services import broadcaster

logger = logging.getLogger(__name__)


async def on_startup(bot: Bot, admin_ids: list[int]):
    await broadcaster.broadcast(bot, admin_ids, "🆙 The bot has been launched!")


def register_global_middlewares(dp: Dispatcher):
    dp.message.middleware(ConfigMessageMiddleware(config))
    dp.callback_query.middleware(ConfigCallbackMiddleware(config))


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )
    logger.info("Starting bot...")

    bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
    await set_commands(bot)

    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    for router in [
        commands_router,
        admin_router,
        start_menu_router,
        search_group_router,
        student_navigation_router,
        search_educator_router,
    ]:
        dp.include_router(router)

    register_global_middlewares(dp)

    await on_startup(bot, config.tg_bot.admin_ids)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("The bot has been disabled!")
