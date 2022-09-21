from tgbot.services.db_api.db_commands import db


async def get_schedule():
    return await db.example()
