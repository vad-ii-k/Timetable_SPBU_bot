from tgbot.services.db_api.db_models import db_gino, User


class DBStatistics:
    @staticmethod
    async def get_number_of_users() -> int:
        number_of_users = await db_gino.func.count(User.user_id).gino.scalar()
        return number_of_users


database_statistics = DBStatistics()
