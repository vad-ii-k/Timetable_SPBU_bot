from aiogram import types

from tgbot.services.db_api.db_models import User


class DBCommands:
    @staticmethod
    async def get_user(tg_user: types.user) -> User:
        user = await User.query.where(User.tg_id == tg_user.id).gino.first()
        return user

    async def add_new_user(self, tg_user: types.user) -> User:
        old_user = await self.get_user(tg_user)
        if old_user:
            return old_user
        new_user = User()
        new_user.tg_id = tg_user.id
        new_user.full_name = tg_user.full_name
        if tg_user.language_code is not "ru":
            new_user.language = "en"
        else:
            new_user.language = "ru"
        new_user.username = tg_user.username
        await new_user.create()
        return new_user


database = DBCommands()
