from tgbot.services.db_api.db_commands import database


async def get_schedule():
    return await database.example()
