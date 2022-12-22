""" Module for launching the bot """
import asyncio
import logging

from redis import asyncio as aioredis
from aiogram import Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.utils.i18n import I18n
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from tgbot.config import app_config, bot
from tgbot.handlers.admin import admin_router
from tgbot.handlers.commands import router as commands_router, set_commands
from tgbot.handlers.errors import router as errors_router
from tgbot.handlers.schedule import router as schedule_router
from tgbot.handlers.searching import router as searching_router
from tgbot.handlers.settings import router as settings_router
from tgbot.handlers.start_menu import router as start_menu_router
from tgbot.handlers.student_navigation import router as student_navigation_router
from tgbot.handlers.unexpected_updates import router as unexpected_updates_router
from tgbot.middlewares.config import ActionMiddleware, LanguageI18nMiddleware, ThrottlingMiddleware
from tgbot.services import broadcaster
from tgbot.services.db_api.db_models import create_db
from tgbot.services.initial_filling_of_groups import adding_groups_to_db
from tgbot.services.notifications import start_scheduler

logger = logging.getLogger(__name__)


async def on_startup(admin_ids: list[int]):
    """
    The function called when the bot is started
    :param admin_ids: admin ids from configs
    """
    await broadcaster.broadcast(bot, admin_ids, "🆙 Бот запущен!\n")


async def register_global_middlewares(dispatcher: Dispatcher, i18n: I18n):
    """
    Setting the necessary [middlewares](https://docs.aiogram.dev/en/dev-3.x/dispatcher/middlewares.html)
    for the [dispatcher](https://docs.aiogram.dev/en/dev-3.x/dispatcher/dispatcher.html)
    :param dispatcher:
    :param i18n:
    """
    dispatcher.message.middleware()
    dispatcher.callback_query.middleware(ActionMiddleware(app_config))
    dispatcher.callback_query.middleware(ThrottlingMiddleware())
    dispatcher.update.outer_middleware(LanguageI18nMiddleware(i18n))


async def main():
    """ Configuring and launching the bot """
    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )
    root_logger = logging.getLogger("gino")
    if root_logger.level == logging.NOTSET:
        root_logger.setLevel(logging.WARN)
    logger.info("Starting bot...")

    await create_db()
    if not app_config.database.are_groups_collected:
        await adding_groups_to_db()

    await set_commands(bot)

    redis = aioredis.Redis(
        host=app_config.redis.host,
        port=app_config.redis.port,
        password=app_config.redis.password,
        db=1
    )
    storage = RedisStorage(redis)
    dispatcher = Dispatcher(storage=storage)

    for router in [
        errors_router,
        commands_router,
        schedule_router,
        admin_router,
        start_menu_router,
        student_navigation_router,
        searching_router,
        settings_router,
        unexpected_updates_router,
    ]:
        dispatcher.include_router(router)

    i18n = I18n(path="tgbot/locales", default_locale="ru", domain="messages")
    await register_global_middlewares(dispatcher, i18n)

    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    await start_scheduler(scheduler)

    await on_startup(app_config.tg_bot.admin_ids)
    await dispatcher.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("The bot has been disabled!")
