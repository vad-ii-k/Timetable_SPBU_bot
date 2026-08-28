""" Middlewares """

import asyncio
import logging
from contextlib import suppress
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.exceptions import TelegramAPIError, TelegramForbiddenError
from aiogram.types import CallbackQuery, Message, TelegramObject
from aiogram.utils.chat_action import ChatActionSender
from aiogram.utils.i18n import gettext as _

from tgbot.config import bot
from tgbot.handlers.helpers import delete_message

logger = logging.getLogger(__name__)


class SafeChatActionSender(ChatActionSender):
    """ChatActionSender без необработанных таймаутов Telegram в фоновой задаче."""

    async def _worker(self) -> None:
        try:
            await super()._worker()
        except TelegramAPIError as err:
            logger.warning("ChatActionSender: %s", err)


class ActionMiddleware(BaseMiddleware):
    """
    Middleware for setting [Chat action sender](https://docs.aiogram.dev/en/dev-3.x/utils/chat_action.html)

    It is needed to handle events with a potentially long response
    """

    def __init__(self, config) -> None:
        """
        :param config:
        """
        self.config = config

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: CallbackQuery | Message,
        data: dict[str, Any],
    ) -> Any:
        """
        :param handler:
        :param event:
        :param data:
        :return:
        """
        data["config"] = self.config
        action = get_flag(data, "chat_action")
        if not action:
            return await handler(event, data)
        message = event.message if isinstance(event, CallbackQuery) else event
        # Forbidden только на chat action; NetworkError хендлера не глотать
        with suppress(TelegramForbiddenError):
            async with SafeChatActionSender(bot=bot, action=action, chat_id=message.chat.id):
                try:
                    return await asyncio.wait_for(handler(event, data), timeout=110)
                except asyncio.TimeoutError:
                    if isinstance(event, CallbackQuery):
                        await delete_message(message)
                    return await message.answer(_("⚠ Превышено время ожидания ответа :(\n" "🔄 Попробуйте снова❕"))
