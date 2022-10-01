from aiogram import types
from sqlalchemy import asc

from tgbot.services.db_api.db_models import User, Settings, Group


class DBCommands:
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
    async def get_user(tg_user_id: int) -> User:
        user = await User.query.where(User.tg_id == tg_user_id).gino.first()
        return user

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

    async def add_new_group(self, group_tt_id: int, group_name: str) -> None:
        old_group = await self.get_group(group_tt_id)
        if old_group:
            return
        new_group = Group()
        new_group.tt_id = group_tt_id
        new_group.name = group_name
        await new_group.create()

    @staticmethod
    async def get_group(group_tt_id: int) -> Group:
        group = await Group.query.where(Group.tt_id == group_tt_id).gino.first()
        return group

    @staticmethod
    async def get_groups_by_name(group_name: str) -> list[Group]:
        groups = await Group.query.where(Group.name.contains(group_name)).order_by(asc(Group.name)).gino.all()
        return groups


database = DBCommands()
