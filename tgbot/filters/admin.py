""" Module with admin filter """

from aiogram.filters import BaseFilter
from aiogram.types import Message

from tgbot.config import app_config


class AdminFilter(BaseFilter):
    """Custom filter to check if the user is an administrator"""

    is_admin: bool = True
    """ Is the user an admin """

    async def __call__(self, obj: Message) -> bool:
        return (obj.from_user.id in app_config.tg_bot.admin_ids) == self.is_admin
