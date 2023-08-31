from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _
from cashews import cache


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
        data: dict[str, Any],
    ) -> Any:
        """
        :param handler:
        :param event:
        :param data:
        :return:
        """
        is_user_in_sl = await self.stop_list_of_users.get(str(event.message.chat.id), default=False)
        if is_user_in_sl:
            await event.answer(_("⚠️ Больше одного действия за секунду!"))
            return
        await self.stop_list_of_users.set(key=str(event.message.chat.id), value=True, expire=1)
        return await handler(event, data)
