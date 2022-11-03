from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile

from tgbot.config import bot
from tgbot.filters.admin import AdminFilter
from tgbot.services.broadcaster import broadcast
from tgbot.services.db_api.db_commands import database
from tgbot.services.db_api.db_statistics import database_statistics
from tgbot.services.statistics import collecting_statistics

admin_router = Router()
admin_router.message.filter(AdminFilter())


@admin_router.message(Command("broadcast"))
async def broadcast_news(message: Message):
    tg_ids = await database.get_tg_ids_of_users()
    news = message.text.split(' ', maxsplit=1)[1]
    await broadcast(bot, users_ids=tg_ids, text=news, disable_notification=True)


@admin_router.message(Command("statistics"))
async def get_statistics(message: Message):
    number_of_users = await database_statistics.get_number_of_users()
    full_statistics = await database_statistics.get_full_statistics()
    await collecting_statistics(full_statistics)
    await message.answer_document(document=FSInputFile('data/statistics.csv'),
                                  caption=f"Количество пользователей: {number_of_users}")
