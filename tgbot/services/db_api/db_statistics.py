""" Statistical work with the database """
from sqlalchemy import asc

from tgbot.services.db_api.db_models import MainScheduleInfo, Settings, User, db_gino
from tgbot.services.statistics import UserStatistics


class DBStatistics:
    """Commands for getting statistics from the database"""

    @staticmethod
    async def get_tg_ids_of_users() -> list[int]:
        """
        Get telegram IDs of all bot users
        :return:
        """
        users = await User.select("tg_id").gino.all()
        users_tg_ids = list(map(lambda user: user[0], users))
        return users_tg_ids

    @staticmethod
    async def get_number_of_users() -> int:
        """
        Get the number of bot users
        :return:
        """
        number_of_users = await db_gino.func.count(User.user_id).gino.scalar()
        return number_of_users

    @staticmethod
    async def get_full_statistics() -> list[UserStatistics]:
        """
        Get information about bot users
        :return:
        """
        full_users_info = (
            await User.join(Settings)
            .join(MainScheduleInfo, isouter=True)
            .select()
            .order_by(asc(User.start_date))
            .gino.all()
        )
        return list(
            map(
                lambda user: UserStatistics(user[3], user[4], user[14], user[15], user[8], user[10], user[11], user[5]),
                full_users_info,
            )
        )


database_statistics = DBStatistics()
