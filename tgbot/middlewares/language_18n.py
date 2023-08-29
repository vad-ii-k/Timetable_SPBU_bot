from typing import Any

from aiogram.types import TelegramObject, User
from aiogram.utils.i18n import I18nMiddleware

from tgbot.services.db_api.db_commands import database


class LanguageI18nMiddleware(I18nMiddleware):
    """Custom [I18nMiddleware](https://docs.aiogram.dev/en/dev-3.x/utils/i18n.html#i18nmiddleware)"""

    async def get_locale(self, event: TelegramObject, data: dict[str, Any]):
        """
        Redefining the method of getting the locale from the database
        :param event:
        :param data:
        :return:
        """
        tg_user: User = data.get("event_from_user")
        user = await database.get_user(tg_user_id=tg_user.id)
        if user is None:
            user = await database.add_new_user(tg_user=tg_user)
        settings = await database.get_settings(user)
        return settings.language
