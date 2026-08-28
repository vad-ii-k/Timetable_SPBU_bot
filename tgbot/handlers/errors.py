"""
Handling all errors
with [ErrorHandler](https://docs.aiogram.dev/en/dev-3.x/dispatcher/class_based_handlers/error.html)
"""

import logging

from aiogram import Router
from aiogram.exceptions import TelegramAPIError, TelegramBadRequest, TelegramForbiddenError, TelegramNetworkError
from aiogram.types.error_event import ErrorEvent

from tgbot.config import app_config, bot
from tgbot.services import broadcaster
from tgbot.services.db_api.db_commands import database
from tgbot.services.timetable_api.api_request import TimetableApiError

router = Router()
logger = logging.getLogger(__name__)

# Просроченный callback: расписание могло уже отправиться, пользователю/админам не шлём алерт
_STALE_CALLBACK_MARKER = "query is too old"


async def _answer_user(update, text: str) -> None:
    try:
        if update.message is not None:
            await update.message.answer(text)
        elif update.callback_query is not None and update.callback_query.message is not None:
            await update.callback_query.message.answer(text)
    except TelegramAPIError:
        logger.warning("Не удалось отправить сообщение об ошибке пользователю")


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
        logger.warning("Пользователь заблокировал бота, пропускаем: %s", err)
        tg_user = update.event_from_user
        if tg_user is not None:
            await database.set_bot_blocked(tg_user.id)
        return

    if isinstance(err, TelegramNetworkError):
        logger.warning("Таймаут Telegram: %s", err)
        return

    if isinstance(err, TelegramBadRequest) and _STALE_CALLBACK_MARKER in str(err).lower():
        logger.warning("Просроченный callback query, пропускаем: %s", err)
        return

    if isinstance(err, TimetableApiError):
        logger.warning("TT API: %s", err)
        await _answer_user(update, "⚠ Расписание временно недоступно. Попробуйте ещё раз через минуту.")
        return

    await _answer_user(update, "⚠ Произошла ошибка :(")
    await broadcaster.broadcast(bot, app_config.tg_bot.admin_ids, f"<code>{str(err)[:4080]}</code>")
    logger.error("%s", err, exc_info=err)
