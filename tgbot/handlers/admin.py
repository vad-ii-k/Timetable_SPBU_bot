from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from tgbot.config import bot
from tgbot.filters.admin import AdminFilter
from tgbot.services.broadcaster import broadcast
from tgbot.services.db_api.db_commands import database

admin_router = Router()
admin_router.message.filter(AdminFilter())


@admin_router.message(Command("broadcast"))
async def broadcast_news(message: Message):
    tg_ids = await database.get_tg_ids_of_users()
    news = message.text.split(' ', maxsplit=1)[1]
    await broadcast(bot, users_ids=tg_ids, text=news, disable_notification=True)
