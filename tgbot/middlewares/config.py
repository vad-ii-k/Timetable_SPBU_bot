from typing import Callable, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import Message, CallbackQuery, TelegramObject, User
from aiogram.utils.chat_action import ChatActionSender
from aiogram.utils.i18n import I18nMiddleware

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
            chat_id = event.message.chat.id
        else:
            chat_id = event.chat.id
        async with ChatActionSender(action=action, chat_id=chat_id):
            return await handler(event, data)


class LanguageI18nMiddleware(I18nMiddleware):
    async def get_locale(self, event: TelegramObject, data: dict[str, Any]):
        tg_user: User = data.get('event_from_user')
        user = await database.get_user(tg_user_id=tg_user.id)
        if user is None:
            user = await database.add_new_user(tg_user=tg_user)
        settings = await database.get_settings(user)
        return settings.language
