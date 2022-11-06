import logging

from aiogram import Router
from aiogram.exceptions import AiogramError, TelegramAPIError
from aiogram.types.error_event import ErrorEvent

from tgbot.config import bot, app_config
from tgbot.services import broadcaster

router = Router()


@router.errors()
async def errors_handler(exception: ErrorEvent):
    update = exception.update
    if update.message is not None:
        await update.message.answer("⚠ Произошла ошибка :(")
    else:
        await update.callback_query.message.answer("⚠ Произошла ошибка :(")
    await broadcaster.broadcast(bot, app_config.tg_bot.admin_ids, f"<code>{str(exception.exception)[:4080]}</code>")

    if isinstance(exception, AiogramError):
        logging.exception("⚠ AiogramError")
        return True
    if isinstance(exception, TelegramAPIError):
        logging.exception("⚠ TelegramAPIError")
        return True

    logging.exception("Update: %s \n%s", update, exception)
