import asyncio

from aiogram.types import Message

from tgbot.config import ADMINS
from tgbot.loader import dp, db


@dp.message_handler(user_id=ADMINS[0], commands=["mailing"])
async def admin_mailing(message: Message):
    tg_ids = await db.get_tg_ids_of_users()
    news = message.get_args()
    for tg_id in tg_ids:
        await dp.bot.send_message(chat_id=tg_id, text=news)
        await asyncio.sleep(0.05)
