""" Middlewares """
import asyncio
from typing import Callable, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import CallbackQuery, TelegramObject, User
from aiogram.utils.chat_action import ChatActionSender
from aiogram.utils.i18n import I18nMiddleware, gettext as _
from cashews import cache

from tgbot.config import bot
from tgbot.handlers.helpers import delete_message
from tgbot.services.db_api.db_commands import database


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
            handler: Callable[[CallbackQuery, dict[str, Any]], Awaitable[Any]],
            event: CallbackQuery,
            data: dict[str, Any]
    ) -> Any:
        """
        :param handler:
        :param event:
        :param data:
        :return:
        """
        data['config'] = self.config
        action = get_flag(data, "chat_action")
        if not action:
            return await handler(event, data)
        async with ChatActionSender(bot=bot, action=action, chat_id=event.message.chat.id):
            handler_cor = handler(event, data)
            try:
                return await asyncio.wait_for(handler_cor, timeout=15)
            except asyncio.TimeoutError:
                await delete_message(event.message)
                return await event.message.answer(_("⚠ Превышено время ожидания ответа :(\n"
                                                    "🔄 Попробуйте снова❕"))


class ThrottlingMiddleware(BaseMiddleware):
    """
    Middleware for flood control

    It is needed to handle too frequent button clicks from a single user
    """
    def __init__(self):
        self.stop_list_of_users = cache.setup("mem://")

    async def __call__(
            self,
            handler: Callable[[CallbackQuery, dict[str, Any]], Awaitable[Any]],
            event: CallbackQuery,
            data: dict[str, Any]
    ) -> Any:
        """
        :param handler:
        :param event:
        :param data:
        :return:
        """
        is_user_in_sl = await self.stop_list_of_users.get(str(event.message.chat.id), default=False)
        if is_user_in_sl:
            await event.answer(_('⚠️ Больше одного действия за секунду!'))
            return
        await self.stop_list_of_users.set(key=str(event.message.chat.id), value=True, expire=1)
        return await handler(event, data)


class LanguageI18nMiddleware(I18nMiddleware):
    """ Custom [I18nMiddleware](https://docs.aiogram.dev/en/dev-3.x/utils/i18n.html#i18nmiddleware) """
    async def get_locale(self, event: TelegramObject, data: dict[str, Any]):
        """
        Redefining the method of getting the locale from the database
        :param event:
        :param data:
        :return:
        """
        tg_user: User = data.get('event_from_user')
        user = await database.get_user(tg_user_id=tg_user.id)
        if user is None:
            user = await database.add_new_user(tg_user=tg_user)
        settings = await database.get_settings(user)
        return settings.language
