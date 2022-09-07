import logging

from aiogram import Dispatcher

from .config import ADMINS
from .loader import db


async def on_startup_notify(dp: Dispatcher) -> None:
    for admin in ADMINS:
        try:
            number_of_users = await db.get_number_of_users()
            await dp.bot.send_message(
                chat_id=admin,
                text=f"Бот запущен!\n"
                     f"Количество пользователей: {number_of_users}"
            )

        except Exception as err:
            logging.exception(err)
