""" Functional work with the database """
from datetime import time

from aiogram import types
from sqlalchemy import asc, func

from tgbot.services.schedule.data_classes import UserType
from tgbot.services.db_api.db_models import User, Settings, Group, MainScheduleInfo


class DBCommands:
    """ Database commands for working with the bot """
    async def add_new_user(self, tg_user: types.User) -> User:
        """
        Adding a new user to the database
        :param tg_user: telegram [User](https://core.telegram.org/bots/api#user)
        :return:
        """
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
        """
        Getting a db user by telegram id
        :param tg_user_id:
        :return:
        """
        user = await User.query.where(User.tg_id == tg_user_id).gino.first()
        return user

    @staticmethod
    async def add_settings(user: User, language_code: str) -> None:
        """
        Adding settings for a db user
        :param user:
        :param language_code:
        """
        new_settings = Settings()
        new_settings.user_id = user.user_id
        if language_code != "ru":
            new_settings.language = "en"
        else:
            new_settings.language = "ru"
        await new_settings.create()

    @staticmethod
    async def get_settings(user: User) -> Settings:
        """
        Getting settings for a db user
        :param user:
        :return:
        """
        settings = await Settings.query.where(Settings.user_id == user.user_id).gino.first()
        return settings

    async def get_settings_by_tg_id(self, tg_user_id: int) -> Settings:
        """
        Getting settings for a db user by telegram id
        :param tg_user_id:
        :return:
        """
        user = await self.get_user(tg_user_id)
        settings = await Settings.query.where(Settings.user_id == user.user_id).gino.first()
        return settings

    async def add_new_group(self, group_tt_id: int, group_name: str) -> None:
        """
        Adding a new group
        :param group_tt_id: group timetable id
        :param group_name:
        :return:
        """
        old_group = await self.get_group(group_tt_id)
        if old_group:
            return
        new_group = Group()
        new_group.tt_id = group_tt_id
        new_group.name = group_name
        await new_group.create()

    @staticmethod
    async def get_group(group_tt_id: int) -> Group:
        """
        Getting a group by timetable ID
        :param group_tt_id:
        :return:
        """
        group = await Group.query.where(Group.tt_id == group_tt_id).gino.first()
        return group

    @staticmethod
    async def get_groups_by_name(group_name: str) -> list[Group]:
        """
        Getting a group by name
        :param group_name:
        :return:
        """
        groups = await Group.query.where(func.lower(Group.name).contains(group_name.lower())).\
            order_by(asc(Group.name)).gino.all()
        return groups

    async def set_main_schedule(self, tg_user_id: int, tt_id: int, user_type: UserType, schedule_name: str) -> None:
        """
        Setting the main schedule
        :param tg_user_id:
        :param tt_id:
        :param user_type:
        :param schedule_name:
        """
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
        """
        Get the main schedule of the user by db user ID
        :param user_id:
        :return:
        """
        main_schedule = await MainScheduleInfo.query.where(MainScheduleInfo.user_id == user_id).gino.first()
        return main_schedule

    @staticmethod
    async def get_users_with_sign_to_summary(current_time: time) -> list[tuple[int, UserType, int]]:
        """
        Getting users with a subscription to the daily summary at the moment
        :param current_time:
        :return:
        """
        users = await Settings.select("user_id").where(Settings.daily_summary == current_time).gino.all()
        users_ids = list(map(lambda user: user[0], users))
        main_schedule_of_users = await User.join(MainScheduleInfo, User.user_id == MainScheduleInfo.user_id).select(). \
            where(MainScheduleInfo.user_id.in_(users_ids)).gino.all()
        user_with_main_schedule = list(map(
            lambda user: (user[1], UserType.STUDENT if user[7] else UserType.EDUCATOR, user[6]), main_schedule_of_users
        ))
        return user_with_main_schedule


database = DBCommands()
