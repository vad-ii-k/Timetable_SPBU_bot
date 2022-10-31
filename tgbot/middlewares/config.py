import asyncio
from typing import Callable, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import Message, CallbackQuery, TelegramObject, User
from aiogram.utils.chat_action import ChatActionSender
from aiogram.utils.i18n import I18nMiddleware, gettext as _

from tgbot.handlers.helpers import delete_message
from tgbot.services.db_api.db_commands import database


class ActionMiddleware(BaseMiddleware):
    def __init__(self, config) -> None:
        self.config = config

    async def __call__(
            self,
            handler: Callable[[Message | CallbackQuery, dict[str, Any]], Awaitable[Any]],
            event: Message | CallbackQuery,
            data: dict[str, Any]
    ) -> Any:
        data['config'] = self.config
        action = get_flag(data, "chat_action")
        if not action:
            return await handler(event, data)
        if isinstance(event, CallbackQuery):
            event_message = event.message
        else:
            event_message = event
        async with ChatActionSender(action=action, chat_id=event_message.chat.id):
            handler_cor = handler(event, data)
            try:
                return await asyncio.wait_for(handler_cor, timeout=15)
            except asyncio.TimeoutError:
                await delete_message(event_message)
                return await event_message.answer(_("⚠ Превышено время ожидания ответа :(\n"
                                                    "🔄 Попробуйте снова❕"))


class LanguageI18nMiddleware(I18nMiddleware):
    async def get_locale(self, event: TelegramObject, data: dict[str, Any]):
        tg_user: User = data.get('event_from_user')
        user = await database.get_user(tg_user_id=tg_user.id)
        if user is None:
            user = await database.add_new_user(tg_user=tg_user)
        settings = await database.get_settings(user)
        return settings.language
