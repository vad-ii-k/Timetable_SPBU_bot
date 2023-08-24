"""
Handling all errors
with [ErrorHandler](https://docs.aiogram.dev/en/dev-3.x/dispatcher/class_based_handlers/error.html)
"""
import logging

from aiogram import Router
from aiogram.exceptions import AiogramError, TelegramAPIError
from aiogram.types.error_event import ErrorEvent

from tgbot.config import app_config, bot
from tgbot.services import broadcaster

router = Router()


@router.errors()
async def errors_handler(exception: ErrorEvent):
    """
    Error handler
    :param exception:
    [ErrorEvent](https://docs.aiogram.dev/en/dev-3.x/api/types/error_event.html#module-aiogram.types.error_event) object
    :return:
    """
    update = exception.update
    error_message = "⚠ Произошла ошибка :("
    if update.message is not None:
        await update.message.answer(error_message)
    else:
        await update.callback_query.message.answer(error_message)
    await broadcaster.broadcast(bot, app_config.tg_bot.admin_ids, f"<code>{str(exception.exception)[:4080]}</code>")

    if isinstance(exception, AiogramError):
        logging.exception("⚠ AiogramError")
        return
    if isinstance(exception, TelegramAPIError):
        logging.exception("⚠ TelegramAPIError")
        return

    logging.exception("Update: %s \n%s", update, exception)
