from tgbot.services.db_api.db_models import User


class DBCommands:
    @staticmethod
    async def example():
        return User.__tablename__


db = DBCommands()
