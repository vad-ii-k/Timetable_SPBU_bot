from sqlalchemy import asc

from tgbot.services.db_api.db_models import db_gino, User, Settings, MainScheduleInfo
from tgbot.services.statistics import UserStatistics


class DBStatistics:
    @staticmethod
    async def get_number_of_users() -> int:
        number_of_users = await db_gino.func.count(User.user_id).gino.scalar()
        return number_of_users

    @staticmethod
    async def get_full_statistics() -> list[UserStatistics]:
        full_users_info = await User.join(Settings).join(MainScheduleInfo).select().\
            order_by(asc(User.start_date)).gino.all()
        return list(map(
            lambda user: UserStatistics(user[3], user[4], user[14], user[7], user[9], user[10]), full_users_info
        ))


database_statistics = DBStatistics()
