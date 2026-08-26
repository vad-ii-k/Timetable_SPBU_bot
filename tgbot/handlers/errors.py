"""
Handling all errors
with [ErrorHandler](https://docs.aiogram.dev/en/dev-3.x/dispatcher/class_based_handlers/error.html)
"""

import logging

from aiogram import Router
from aiogram.exceptions import AiogramError, TelegramAPIError, TelegramBadRequest, TelegramForbiddenError
from aiogram.types.error_event import ErrorEvent

from tgbot.config import app_config, bot
from tgbot.services import broadcaster
from tgbot.services.db_api.db_commands import database

router = Router()

# Просроченный callback: расписание могло уже отправиться, пользователю/админам не шлём алерт
_STALE_CALLBACK_MARKER = "query is too old"


@router.errors()
async def errors_handler(exception: ErrorEvent):
    """
    Error handler
    :param exception:
    [ErrorEvent](https://docs.aiogram.dev/en/dev-3.x/api/types/error_event.html#module-aiogram.types.error_event) object
    :return:
    """
    update = exception.update
    err = exception.exception

    if isinstance(err, TelegramForbiddenError):
        logging.warning("Пользователь заблокировал бота, пропускаем: %s", err)
        tg_user_id = None
        if update.message is not None and update.message.from_user is not None:
            tg_user_id = update.message.from_user.id
        elif update.callback_query is not None:
            tg_user_id = update.callback_query.from_user.id
        if tg_user_id is not None:
            db_user = await database.get_user(tg_user_id)
            if db_user is not None:
                await db_user.update(is_bot_blocked=True).apply()
        return

    if isinstance(err, TelegramBadRequest) and _STALE_CALLBACK_MARKER in str(err).lower():
        logging.warning("Просроченный callback query, пропускаем: %s", err)
        return

    error_message = "⚠ Произошла ошибка :("
    try:
        if update.message is not None:
            await update.message.answer(error_message)
        elif update.callback_query is not None and update.callback_query.message is not None:
            await update.callback_query.message.answer(error_message)
    except TelegramAPIError:
        logging.warning("Не удалось отправить сообщение об ошибке пользователю")
    await broadcaster.broadcast(bot, app_config.tg_bot.admin_ids, f"<code>{str(err)[:4080]}</code>")

    if isinstance(err, AiogramError):
        logging.exception("⚠ AiogramError")
        return
    if isinstance(err, TelegramAPIError):
        logging.exception("⚠ TelegramAPIError")
        return

    logging.exception("Update: %s \n%s", update, exception)
