from aiogram import types

from tgbot.services.db_api.db_models import User, Settings


class DBCommands:
    @staticmethod
    async def get_user(tg_user_id: int) -> User:
        user = await User.query.where(User.tg_id == tg_user_id).gino.first()
        return user

    async def add_new_user(self, tg_user: types.User) -> User:
        old_user = await self.get_user(tg_user.id)
        if old_user:
            return old_user
        new_user = User()
        new_user.tg_id = tg_user.id
        new_user.full_name = tg_user.full_name
        new_user.username = tg_user.username
        await new_user.create()
        await self.add_settings(new_user, tg_user.language_code)
        return new_user

    @staticmethod
    async def add_settings(user: User, language_code: str):
        new_settings = Settings()
        new_settings.user_id = user.user_id
        if language_code != "ru":
            new_settings.language = "en"
        else:
            new_settings.language = "ru"
        await new_settings.create()

    @staticmethod
    async def get_settings(user: User) -> Settings:
        settings = await Settings.query.where(Settings.user_id == user.user_id).gino.first()
        return settings


database = DBCommands()
