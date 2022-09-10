import asyncio
import logging
from contextlib import suppress

from aiogram.types import Message
from aiogram.utils.exceptions import TelegramAPIError

from tgbot.config import ADMINS
from tgbot.loader import dp, db


@dp.message_handler(user_id=ADMINS[0], commands=["broadcast"])
async def broadcast_news(message: Message):
    count = 0
    tg_ids = await db.get_tg_ids_of_users()
    news = message.get_args()
    for tg_id in tg_ids:
        with suppress(TelegramAPIError):
            await dp.bot.send_message(chat_id=tg_id, text=news)
            await asyncio.sleep(0.1)
            count += 1
    logging.info(f"{count}/{len(tg_ids)} users received messages")
