import logging

from aiogram import Dispatcher

from .config import ADMINS


async def on_startup_notify(dp: Dispatcher) -> None:
    for admin in ADMINS:
        try:
            await dp.bot.send_message(admin, "Бот Запущен")

        except Exception as err:
            logging.exception(err)
