from datetime import time

from aiogram import types
from sqlalchemy import asc

from tgbot.misc.states import UserType
from tgbot.services.db_api.db_models import User, Settings, Group, MainScheduleInfo


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

    async def get_settings_by_tg_id(self, tg_user_id: int) -> Settings:
        user = await self.get_user(tg_user_id)
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

    async def set_main_schedule(self, tg_user_id: int, tt_id: int, user_type: UserType, schedule_name) -> None:
        user = await self.get_user(tg_user_id)
        old_main_schedule = await self.get_main_schedule(user.user_id)
        if old_main_schedule:
            await MainScheduleInfo.delete.where(MainScheduleInfo.user_id == user.user_id).gino.status()
        new_main_schedule = MainScheduleInfo()
        new_main_schedule.user_id = user.user_id
        new_main_schedule.timetable_id = tt_id
        new_main_schedule.user_type_is_student = (user_type == UserType.STUDENT)
        new_main_schedule.name = schedule_name
        await new_main_schedule.create()

    @staticmethod
    async def get_main_schedule(user_id: int) -> MainScheduleInfo:
        main_schedule = await MainScheduleInfo.query.where(MainScheduleInfo.user_id == user_id).gino.first()
        return main_schedule

    @staticmethod
    async def get_users_with_sign_to_summary(current_time: time) -> list[tuple[int, UserType, int]]:
        users = await Settings.select("user_id").where(Settings.daily_summary == current_time).gino.all()
        users_ids = list(map(lambda user: user[0], users))
        main_schedule_of_users = await User.join(MainScheduleInfo, User.user_id == MainScheduleInfo.user_id).select(). \
            where(MainScheduleInfo.user_id.in_(users_ids)).gino.all()
        user_with_main_schedule = list(map(
            lambda user: (user[1], UserType.STUDENT if user[7] else UserType.EDUCATOR, user[6]), main_schedule_of_users
        ))
        return user_with_main_schedule

    @staticmethod
    async def get_tg_ids_of_users() -> list[int]:
        users = await User.select("tg_id").gino.all()
        users_tg_ids = list(map(lambda user: user[0], users))
        return users_tg_ids


database = DBCommands()
