from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import Message, CallbackQuery, TelegramObject, User
from aiogram.utils.chat_action import ChatActionSender
from aiogram.utils.i18n import I18nMiddleware

from tgbot.services.db_api.db_commands import database


class ConfigMessageMiddleware(BaseMiddleware):
    def __init__(self, config) -> None:
        self.config = config

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        data['config'] = self.config
        action = get_flag(data, "chat_action")
        if not action:
            return await handler(event, data)
        async with ChatActionSender(action=action, chat_id=event.chat.id):
            return await handler(event, data)


class ConfigCallbackMiddleware(BaseMiddleware):
    def __init__(self, config) -> None:
        self.config = config

    async def __call__(
            self,
            handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
            event: CallbackQuery,
            data: Dict[str, Any]
    ) -> Any:
        data['config'] = self.config
        action = get_flag(data, "chat_action")
        if not action:
            return await handler(event, data)
        async with ChatActionSender(action=action, chat_id=event.message.chat.id):
            return await handler(event, data)


class LanguageI18nMiddleware(I18nMiddleware):
    async def get_locale(self, event: TelegramObject, data: Dict[str, Any]):
        tg_user: User = data.get('event_from_user')
        user = await database.get_user(tg_user_id=tg_user.id)
        settings = await database.get_settings(user)
        return settings.language
