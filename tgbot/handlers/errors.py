import logging

from aiogram import Router
from aiogram.exceptions import AiogramError, TelegramAPIError
from aiogram.types import Update

from tgbot.config import bot, app_config
from tgbot.services import broadcaster

router = Router()


@router.errors()
async def errors_handler(update: Update, exception: Exception):
    if update.message is not None:
        await update.message.answer("⚠ Произошла ошибка :(")
    else:
        await update.callback_query.message.answer("⚠ Произошла ошибка :(")
    await broadcaster.broadcast(bot, app_config.tg_bot.admin_ids, f"<code>{update}</code>", True)

    if isinstance(exception, AiogramError):
        logging.exception("⚠ AiogramError")
        return True
    if isinstance(exception, TelegramAPIError):
        logging.exception("⚠ TelegramAPIError")
        return True

    logging.exception("Update: %s \n%s", update, exception)